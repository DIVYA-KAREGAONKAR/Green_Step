import datetime
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.db.models import Sum
from django.db.models.functions import TruncMonth

from .models import CarbonEntry, Category, Profile
from .forms import ExtendedRegisterForm
from .utils import render_to_pdf
@login_required
def delete_entry(request, entry_id):
    entry = get_object_or_404(CarbonEntry, id=entry_id, user=request.user)
    if request.method == "POST":
        entry.delete()
    return redirect('dashboard')
@login_required
def export_pdf(request):
    user_entries = CarbonEntry.objects.filter(user=request.user).order_by('-created_at')
    total = user_entries.aggregate(Sum('co2_total'))['co2_total__sum'] or 0
    
    context = {
        'user': request.user,
        'entries': user_entries,
        'total': total,
        'dept': request.user.profile.get_department_display(),
        'date': datetime.datetime.now(),
    }
    
    pdf = render_to_pdf('core/audit_report.html', context)
    if pdf:
        response = HttpResponse(pdf, content_type='application/pdf')
        filename = f"Audit_Report_{request.user.username}.pdf"
        content = f"attachment; filename='{filename}'"
        response['Content-Disposition'] = content
        return response
    return HttpResponse("Error generating PDF", status=400)
@login_required
def dashboard(request):
    # 1. Fetch user-specific entries
    user_entries = CarbonEntry.objects.filter(user=request.user).order_by('-created_at')
    user_total = user_entries.aggregate(Sum('co2_total'))['co2_total__sum'] or 0
    
    # 2. Chart Telemetry
    breakdown = user_entries.values('category__name').annotate(total=Sum('co2_total'))
    circle_labels = [item['category__name'] for item in breakdown]
    circle_values = [float(item['total']) for item in breakdown]

    # 3. Departmental Context (Requires Profile)
    try:
        profile = request.user.profile
        dept_code = profile.department
        dept_name = profile.get_department_display()
    except Profile.DoesNotExist:
        dept_code, dept_name = 'ENG', 'Engineering'

    dept_total = CarbonEntry.objects.filter(
        user__profile__department=dept_code
    ).aggregate(Sum('co2_total'))['co2_total__sum'] or 0

    personal_share = (user_total / dept_total * 100) if dept_total > 0 else 0

    context = {
        'metrics': {
            'total': round(user_total, 2),
            'trees': round(user_total / 21, 1),
            'dept_name': dept_name,
            'dept_code': dept_code,
            'dept_total': round(dept_total, 2),
            'personal_share': round(personal_share, 1),
        },
        'entries': user_entries[:10],
        'circle_labels': circle_labels,
        'circle_values': circle_values,
    }
    return render(request, 'core/dashboard.html', context)
def register_view(request):
    if request.method == "POST":
        form = ExtendedRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Save the department to the profile
            user.profile.department = form.cleaned_data.get('department')
            user.profile.save()
            
            login(request, user)
            return redirect('dashboard')
    else:
        form = ExtendedRegisterForm()
    return render(request, 'core/register.html', {'form': form})
def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            
            # Use 'next' from the URL, or default to 'dashboard'
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('dashboard') # Force redirect to dashboard name
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

@login_required
def log_activity(request):
    if request.method == "POST":
        # 1. Capture form values
        commute_mode = request.POST.get('commute_mode', 'CAR') 
        commute_dist = request.POST.get('commute_dist', '0')
        hours_worked = request.POST.get('hours_worked', '0')
        vcpu_hours = request.POST.get('vcpu_hours', '0')

        # 2. Define log_data INSIDE the POST block
        log_data = [
            (commute_dist, commute_mode),          
            (hours_worked, 'Office Energy'),      
            (vcpu_hours, 'Cloud Infrastructure')  
        ]

        # 3. Run the loop ONLY during a POST request
        for value, cat_name in log_data:
            try:
                float_val = float(value) if value else 0
                if float_val > 0:
                    category = Category.objects.get(name__iexact=cat_name)
                    CarbonEntry.objects.create(
                        user=request.user,
                        category=category,
                        value=float_val
                    )
                    print(f"DEBUG: Saved {float_val} for {cat_name}")
            except (Category.DoesNotExist, ValueError):
                print(f"DEBUG: Skipping {cat_name} - check Admin categories.")
        
        return redirect('dashboard')

    # This part handles the GET request (just showing the page)
    return render(request, 'core/log_activity.html')

@login_required
def history(request):
    entries = CarbonEntry.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'core/history.html', {'entries': entries})