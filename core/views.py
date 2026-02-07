
from django.shortcuts import redirect, render
from .models import CarbonEntry, Category
from .services.carbon_logic import calculate_metrics
from django.contrib.auth.decorators import login_required

@login_required
def dashboard(request):
    user_entries = CarbonEntry.objects.filter(user=request.user)
    metrics = calculate_metrics(user_entries)
    categories = Category.objects.all()
    
    return render(request, 'core/dashboard.html', {
        'metrics': metrics,
        'entries': user_entries.order_by('-created_at'),
        'categories': categories
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