from django.shortcuts import render


def landing_view(request):
    if request.user.is_authenticated:
        from django.shortcuts import redirect
        return redirect('dashboard:home')
    return render(request, 'accounts/landing.html')
