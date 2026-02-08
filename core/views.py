
from django.shortcuts import redirect, render
from .models import CarbonEntry, Category
from .services.carbon_logic import calculate_metrics
from django.contrib.auth.decorators import login_required
from django.db.models.functions import TruncMonth
from django.db.models import Sum
from .models import CarbonEntry
from django.shortcuts import render
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm


@login_required
def dashboard(request):
    # Fetch entries for the current user
    entries = CarbonEntry.objects.filter(user=request.user).order_by('-created_at')
    
    # Logic to get breakdown by category for the Intensity Split circle
    breakdown = entries.values('category__name').annotate(total=Sum('co2_total'))
    
    circle_labels = [item['category__name'] for item in breakdown]
    circle_values = [float(item['total']) for item in breakdown]

    context = {
        'entries': entries[:5], # Show last 5 logs
        'metrics': {
            'total': entries.aggregate(Sum('co2_total'))['co2_total__sum'] or 0,
            'trees': (entries.aggregate(Sum('co2_total'))['co2_total__sum'] or 0) / 21,
        },
        'circle_labels': circle_labels,
        'circle_values': circle_values,
    }
    return render(request, 'core/dashboard.html', context)


def register_view(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = UserCreationForm()
    return render(request, 'core/register.html', {'form': form})

def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)  # This creates the session!
            # Use 'next' if it exists, otherwise go to dashboard
            next_url = request.GET.get('next', 'dashboard')
            return redirect(next_url)
        else:
            # Print errors to terminal to see why it's failing
            print(form.errors) 
    else:
        form = AuthenticationForm()
    return render(request, 'core/login.html', {'form': form})





def monthly_trends(request):
    # Aggregate data
    monthly_data = (
        CarbonEntry.objects.filter(user=request.user)
        .annotate(month=TruncMonth('created_at'))
        .values('month')
        .annotate(total_co2=Sum('co2_total'))
        .order_by('month')
    )

    # Convert to clean lists for JavaScript
    labels = [data['month'].strftime("%b %Y") for data in monthly_data]
    values = [float(data['total_co2']) for data in monthly_data] # Ensure float type

    return render(request, 'core/trends.html', {
        'labels': labels,
        'values': values,
        'monthly_data': monthly_data
    })

def log_activity(request):
    if request.method == "POST":
        mode = request.POST.get('category_mode')
        value = float(request.POST.get('value'))

        if mode == 'manual':
            # Create a brand new category on the fly
            name = request.POST.get('custom_name')
            unit = request.POST.get('custom_unit')
            factor = float(request.POST.get('custom_factor'))
            category, _ = Category.objects.get_or_create(
                name=name, 
                defaults={'unit': unit, 'co2_per_unit': factor}
            )
        else:
            # Use the existing selection
            category_id = request.POST.get('category_id')
            category = Category.objects.get(id=category_id)
            factor = category.co2_per_unit

        CarbonEntry.objects.create(
            user=request.user,
            category=category,
            value=value,
            co2_total=value * factor
        )
        return redirect('dashboard')

    categories = Category.objects.all()
    return render(request, 'core/log_activity.html', {'categories': categories})
def history(request):
    entries = CarbonEntry.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'core/history.html', {'entries': entries})