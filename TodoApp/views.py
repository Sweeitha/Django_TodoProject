from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
#an form we can use from django
from django.contrib.auth.models import User
#to create and save the users in db
from django.db import IntegrityError
from django.contrib.auth import login, logout, authenticate
from .models import Todo
from .forms import TodoForm
from django.utils import timezone
from django.contrib.auth.decorators import login_required#to handle when loggedout user try to access other pages by changing path.also add login_url in setting to handle in better way

def home(request):
    return render(request, 'Todo/home.html')

def signupuser(request):
    if request.method == 'GET':
        #returns the signup page to enter details
        return render(request, 'Todo/signup.html', {'form':UserCreationForm()})
    else:
        #checks if passwords match
        if request.POST['password1'] == request.POST['password2']:
            try:
                #create an user and login
                user = User.objects.create_user(request.POST['username'], password = request.POST['password1'])
                user.save()
                login(request, user)
                return redirect('currenttodo')
            except IntegrityError:
                #if user already exits Integrity error will occur so display this error and signup page
                return render(request, 'Todo/signup.html', {'form':UserCreationForm(), 'error':'Username already exists! Please give a new Username'})
        #if password mismatch display this error and signup page
        else:
            return render(request, 'Todo/signup.html', {'form':UserCreationForm(), 'error':'Your Passwords did not match'})

def loginuser(request):
    if request.method == 'GET':
        #returns the login page to enter details
        return render(request, 'Todo/login.html', {'form':AuthenticationForm()})
    else:
        user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
        if user is None:
            return render(request, 'Todo/login.html', {'form':AuthenticationForm(), 'error':'Username/Password is incorrect'})
        else:
            login(request, user)
            return redirect('currenttodo')

@login_required
def logoutuser(request):
    if request.method=='POST':
        logout(request)
        return redirect('home')
@login_required
def createtodo(request):
    if request.method=='GET':
        #shows the create todo form from the customised todoform class in forms.py
        return render(request, 'Todo/createtodo.html', {'form':TodoForm()})
    else:
        try:
            form = TodoForm(request.POST)#gives the input that user enters to todoform
            newtodo = form.save(commit=False)#saves the detail user emtered temporarily but not in db as we are left with user input field
            newtodo.user = request.user#assigning the user as input for field user
            newtodo.save()#now saving in db
            return redirect('currenttodo')
        except ValueError:
            return render(request, 'Todo/createtodo.html', {'form':TodoForm(), 'error':'You have passed a bad input. Try Again.'})
@login_required
def currenttodo(request):
    todos = Todo.objects.filter(user = request.user, datecompleted__isnull = True)
    #only displays the memos of signed in user and only displays the memos that don't have any completion dates
    return render(request, 'Todo/currenttodo.html',{'todos':todos})
@login_required
def completedtodo(request):
    todos = Todo.objects.filter(user = request.user, datecompleted__isnull = False).order_by('-datecompleted')
    #only displays the memos of signed in user and only displays the memos that have completion dates and order_by('-') gives us in desending order
    return render(request, 'Todo/completedtodo.html',{'todos':todos})
@login_required
def viewtodo(request, todo_pk):
    todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)#(classname, primarykey, grabs the todos of only the logged in user)
    if request.method=='GET':
        form = TodoForm(instance=todo)#for the user to update the memo and its inputs
        return render(request, 'Todo/viewtodo.html',{'todo':todo, 'form':form})
    else:
        try:
            form = TodoForm(request.POST, instance=todo)#gives the input that user enters to todoform and passes the userinput with the help of instance
            form.save()
            return redirect('currenttodo')
        except ValueError:
            return render(request, 'Todo/viewtodo.html', {'form':TodoForm(), 'error':'You have passed a bad input. Try Again.'})
@login_required
def completetodo(request, todo_pk):
    todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)
    if request.method=='POST':
        todo.datecompleted = timezone.now()
        todo.save()
        return redirect('currenttodo')
@login_required
def deletetodo(request, todo_pk):
    todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)
    if request.method=='POST':
        todo.delete()
        return redirect('currenttodo')
# Create your views here.
