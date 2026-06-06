from django.contrib.auth import login
from django.shortcuts import redirect, render
from django.contrib.auth.forms import UserCreationForm

def join(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('index')
    else:
        form = UserCreationForm()
    return render(request, 'frontend/join.html', {'form': form})