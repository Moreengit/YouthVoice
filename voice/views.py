from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login  
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.http import Http404
from .forms import RegisterForm, IdeaForm
from .models import Profile, Idea, Vote, Sponsorship
from .mpesa import initiate_stk_push


def home(request):
    total_sponsors = Sponsorship.objects.filter(status='completed').count()
    latest_sponsors = Sponsorship.objects.filter(status='completed').order_by('-created_at')[:10]
    
    # context = {
    #     'total_sponsors': total_sponsors,
    #     'latest_sponsors': latest_sponsors,
    # }
    return render(request, 'voice/landing.html')


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            Profile.objects.create(
                user=user,
                role=form.cleaned_data['role'],
                county=form.cleaned_data['county'],
                constituency=form.cleaned_data['constituency'],
                ward=form.cleaned_data['ward']
            )
            login(request, user)  
            return redirect('home')
    else:
        form = RegisterForm()
    return render(request, 'voice/registration/register.html', {'form': form})


def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            # Redirect based on role
            if hasattr(user, 'profile'):
                if user.profile.role == 'leader':
                    return redirect('leader_profile')   # Leader profile page
                else:
                    return redirect('profile')         # Resident profile page

            # Fallback
            return redirect('profile')

        else:
            messages.error(request, "Invalid username or password.")

    return render(request, 'registration/login.html')



# Profile page
@login_required
def profile(request):

    user_ideas = Idea.objects.filter(author=request.user)
    return render(request, 'voice/profile.html', {
        'ideas': user_ideas,
        'user': request.user 
    })
    """
    Show all ideas posted by the logged-in user.
    """
    user_ideas = Idea.objects.filter(author=request.user)
    return render(request, 'voice/profile.html', {'ideas': user_ideas})

    # return render(request, 'voice/feed.html')  


# Post idea
@login_required
def post_idea(request):
    if request.method == 'POST':
        form = IdeaForm(request.POST, request.FILES)
        if form.is_valid():
            idea = form.save(commit=False)
            idea.author = request.user
            idea.county = request.user.profile.county
            idea.constituency = request.user.profile.constituency
            idea.ward = request.user.profile.ward
            idea.save()
            return redirect('feed')
    else:
        form = IdeaForm()
    return render(request, 'voice/post_idea.html', {'form': form})


# Feed
@login_required
def feed(request):
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        return redirect('profile')

    view = request.GET.get('view', 'ward')

    if view == 'county':
        ideas = Idea.objects.filter(county=profile.county)
    elif view == 'all':
        ideas = Idea.objects.all()
    else:
        ideas = Idea.objects.filter(
            county=profile.county,
            constituency=profile.constituency,
            ward=profile.ward
        )

    for idea in ideas:
        idea.user_has_voted = idea.vote_set.filter(user=request.user).exists()
        idea.total_votes = idea.vote_set.count()

    context = {
        'ideas': ideas.order_by('-created_at'),
        'view': view,
    }
    return render(request, 'voice/feed.html', context)


# Voting
@login_required
def vote_idea(request, idea_id):
    idea = get_object_or_404(Idea, id=idea_id)
    
    # Check if user already voted
    existing_vote = Vote.objects.filter(idea=idea, user=request.user)

    if existing_vote.exists():
        # Already voted → remove vote (unvote)
        existing_vote.delete()
    else:
        # Not voted → add vote
        Vote.objects.create(idea=idea, user=request.user)

    # Refresh vote count
    idea.refresh_from_db()
    total_votes = idea.vote_set.count()
    user_has_voted = idea.vote_set.filter(user=request.user).exists()

    # Return updated button
    html = render_to_string("voice/partials/vote_button.html", {
        "idea": idea,
        "user": request.user,
        "total_votes": total_votes,
        "user_has_voted": user_has_voted,
    }, request=request)

    return HttpResponse(html)


def get_locations(request):
    json_path = os.path.join(settings.BASE_DIR, 'voice', 'data', 'kenya_locations.json')
    try:
        with open(json_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        return JsonResponse(data)
    except FileNotFoundError:
        return JsonResponse({"error": "Locations file not found"}, status=404)



from django.db.models import Count

@login_required
def leader_dashboard(request):
    if request.user.profile.role != 'leader':
        raise Http404("You are not authorized to access the Leader Dashboard")

    leader_ward = request.user.profile.ward

    # Annotate with vote count
    ideas = Idea.objects.filter(ward=leader_ward)\
                        .annotate(vote_count=Count('vote'))\
                        .order_by('-created_at')

    top_ideas = ideas.order_by('-vote_count')[:5]

    
    context = {
        'ideas': ideas,
        'top_ideas': top_ideas,
    }
    return render(request, 'voice/leader_dashboard.html', context)




@login_required
def update_status(request, idea_id):
    if request.user.profile.role != 'leader':
        raise Http404("Only leaders can update status")

    idea = get_object_or_404(Idea, id=idea_id, ward=request.user.profile.ward)

    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in ['open', 'in_progress', 'done']:
            idea.status = new_status
            idea.save()

    return redirect('leader_dashboard')



def sponsor_request(request):
    if request.method == 'POST':
        amount = request.POST.get('amount')
        phone = request.POST.get('phone').replace(' ', '').replace(' ', '')
        name = request.POST.get('name', 'Anonymous')
        message = request.POST.get('message', '')

        if phone.startswith('0'):
            phone = '254' + phone[1:]
        elif not phone.startswith('+254'):
            phone = '+254' + phone


        try:
            response = initiate_stk_push(phone, int(amount))
            if response.get('ResponseCode') == '0':
                Sponsorship.objects.create(
                    name=name,
                    phone_number=phone,
                    amount=amount,
                    message=message,
                    mpesa_receipt_number=response.get('CheckoutRequestID'),
                    status='pending'
                )
                messages.success(request, "Check your phone — enter MPESA PIN to complete!")
            else:
                messages.error(request, "MPESA error. Try again.")
        except Exception as e:
            messages.error(request, "Payment failed. Try again.")

    return redirect('home')





from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
import json
from .models import Sponsorship

@csrf_exempt
def mpesa_confirmation(request):
    """
    Receives M-PESA STK push confirmation from Daraja sandbox.
    Updates the corresponding Sponsorship record.
    """
    if request.method == 'POST':
        try:
            # Decode JSON body
            data = request.body.decode('utf-8')
            result = json.loads(data)

            # Safely get stkCallback
            stk_callback = result.get('Body', {}).get('stkCallback', {})
            result_code = stk_callback.get('ResultCode')

            if result_code == 0:
                # Payment successful
                metadata = stk_callback.get('CallbackMetadata', {}).get('Item', [])

                # Extract receipt number and amount
                receipt_number = next(
                    (x['Value'] for x in metadata if x['Name'] == 'MpesaReceiptNumber'),
                    None
                )
                amount = next(
                    (x['Value'] for x in metadata if x['Name'] == 'Amount'),
                    None
                )

                # Update pending sponsorship record
                try:
                    sponsor = Sponsorship.objects.get(
                        mpesa_receipt_number=stk_callback.get('CheckoutRequestID'),
                        status='pending'
                    )
                    sponsor.mpesa_receipt_number = receipt_number
                    sponsor.amount = amount
                    sponsor.status = 'completed'
                    sponsor.save()
                except Sponsorship.DoesNotExist:
                    # Record not found, maybe log this
                    pass

            else:
                # Payment failed, optionally log failure
                checkout_id = stk_callback.get('CheckoutRequestID')
                # You can update the sponsorship to 'failed' if needed
                try:
                    sponsor = Sponsorship.objects.get(
                        mpesa_receipt_number=checkout_id,
                        status='pending'
                    )
                    sponsor.status = 'failed'
                    sponsor.save()
                except Sponsorship.DoesNotExist:
                    pass

        except Exception as e:
            # Log exception if needed
            print("MPESA confirmation error:", str(e))

    return HttpResponse("OK")


def mpesa_validation(request):
    return HttpResponse("OK")




@login_required
def delete_idea(request, idea_id):
    """
    Delete an idea if the logged-in user is the author.
    """
    idea = get_object_or_404(Idea, id=idea_id, author=request.user)

    if request.method == 'POST':
        idea.delete()
        return redirect('profile')  # Redirect back to profile

    return redirect('profile')



@login_required
def leader_profile(request):
    """
    View for leader's profile page.
    Shows only username and email, no ideas or post options.
    """
    return render(request, 'voice/leader_profile.html')


