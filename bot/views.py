from . import jobs as cron_jobs
from func_timeout import func_timeout, FunctionTimedOut
from django.shortcuts import (redirect, render, get_object_or_404)
from django.contrib.auth.decorators import (login_required)
from django.contrib.auth import (authenticate, login, logout)
from django.contrib import messages
from . import models
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import (reverse_lazy, reverse)
from django.views.generic.edit import (CreateView, UpdateView, DeleteView)
from django.views.generic.detail import DetailView
from django.http import HttpResponseRedirect
from cryptography.fernet import Fernet
from datetime import datetime


def start_TdJob(login_details, thread_title, topic_code, thread_reply, thread_job, nl_account, nl_account_pk, minutes):
    try:
        job = func_timeout(20, cron_jobs.ThreadReplyJob_, args=(login_details, thread_title, topic_code, thread_reply))
    except FunctionTimedOut:
        raise FunctionTimedOut
    cron_jobs.scheduler.add_job(job.spam_thread, 'interval', minutes=int(minutes), id=nl_account_pk, replace_existing=True, max_instances=10)

    #Change has job value
    nl_account.has_job = True

    #Activate Job
    thread_job.activated = True
    thread_job.nl_account_pk = nl_account_pk
    nl_account.save()
    thread_job.save()

def start_BjJob(login_details, board_uri, board_reply, board_job, nl_account, nl_account_pk, minutes):
    try:
        job = func_timeout(25, cron_jobs.BoardReplyJob_, args=(login_details, board_uri, board_reply))
    except FunctionTimedOut:
        raise FunctionTimedOut
    cron_jobs.scheduler.add_job(job.spam_board, 'interval', minutes=int(minutes), id=nl_account_pk)

    #Change has job value
    nl_account.has_job = True
    
    #Activate Job
    board_job.activated = True
    board_job.nl_account_pk = nl_account_pk
    nl_account.save()
    board_job.save()


def start_FpJob(login_details, frontpage_reply, frontpage_job, nl_account, nl_account_pk, seconds):
    try:
        job = func_timeout(25, cron_jobs.FrontPageMonitorJob_, args=(login_details, frontpage_reply))
    except FunctionTimedOut:
        raise FunctionTimedOut
    cron_jobs.scheduler.add_job(job.spam_frontpage, 'interval', seconds=int(seconds), id=nl_account_pk)
    
    #Change has job value
    nl_account.has_job = True

    #Activate Job
    frontpage_job.activated = True
    frontpage_job.nl_account_pk = nl_account_pk
    nl_account.save()
    frontpage_job.save()


@login_required(login_url='/login')
def home(request):
    context = {
            'jobs':len(models.BoardReplyJob.objects.all()) + len(models.ThreadReplyJob.objects.all()) + len(models.FrontPageMonitorJob.objects.all()),
            'nl_accounts':len(models.NairalandAccount.objects.all()),
            'active_jobs':len(models.BoardReplyJob.objects.filter(activated=True)) + len(models.ThreadReplyJob.objects.filter(activated=True)) + len(models.FrontPageMonitorJob.objects.filter(activated=True)),
    }

    return render(request, 'bot/theme/index.html', context)


def loginUser(request):
    if request.method == 'POST':
        username = request.POST['username'].strip()
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request,user)
            return redirect('/')
    return render(request, 'bot/theme/login.html')

def logoutUser(request):
    logout(request)
    return redirect('/login/')

@login_required(login_url='/login/')
def license(request):
    if request.method == 'POST':
        user = request.user
        key = request.POST['key']
        profile = models.Profile.objects.get(user=user)
        expires = key[:120]
        cipher_a = key[120:170]
        cipher_b = key[214:]
        cipher = cipher_a + cipher_b
        p_key = key[170:214]
        now = datetime.timestamp(datetime.now())
        try:
            f = Fernet(p_key.encode())
            plan = f.decrypt(cipher.encode()).decode()
            expires = float(f.decrypt(expires.encode()).decode())
            if now >= expires:
                raise ValueError()
            elif plan == 'STPLAN':
                profile.account_type = 'st'
                profile.license_key = key
                profile.activated = True
                profile.save()
            elif plan == 'PRPLAN':
                profile.account_type = 'pr'
                profile.license_key = key
                profile.activated = True
                profile.save()
            messages.success(request, "Account activated successfully!")
        except:
            messages.warning(request, "Invalid Activation Key!!")
    return render(request, 'bot/theme/license.html')




@login_required(login_url='/login/')
def account(request):
    profile = models.Profile.objects.get(user=request.user)
    return render(request, 'bot/theme/account.html', {'profile':profile})


@login_required(login_url='/login')
def changePassword(request):
    if request.method == 'POST':
        password = request.POST['password']
        user = request.user
        user.set_password(password)
        user.save()
        messages.success(request, "Account password changed successfully.")
    return render(request, 'bot/theme/change.html')


@login_required(login_url="/login/")
def jobs(request):
    board_jobs = models.BoardReplyJob.objects.all()
    thread_jobs = models.ThreadReplyJob.objects.all()
    frontpage_jobs = models.FrontPageMonitorJob.objects.all()
    
    return render(request, 'bot/theme/jobs.html', {'board_jobs':board_jobs, 'thread_jobs':thread_jobs, 'frontpage_jobs':frontpage_jobs})



@login_required(login_url="/login/")
def nl_accounts(request):
    nairaland_accounts = models.NairalandAccount.objects.all()
    return render(request, 'bot/theme/ac.html', {'nairaland_accounts':nairaland_accounts})


@login_required(login_url="/login/")
def activateTdJob(request, pk):
    nl_accounts = models.NairalandAccount.objects.all()
    thread_job = get_object_or_404(models.ThreadReplyJob, ('pk',pk))
    thread_title = thread_job.thread_title
    topic_code = thread_job.topic_code
    thread_reply = thread_job.reply


    if request.method == 'POST':
        nl_account_pk = request.POST['nl_account_pk']
        nl_account = get_object_or_404(models.NairalandAccount, ('pk',nl_account_pk))
        #Check If Account has job
        if nl_account.has_job == True:
            messages.warning(request, "NL Account has a job!!!")
        else:
            minutes = request.POST['minutes']
            login_details = {'name':nl_account.username,'password':nl_account.password}
            try:
                start_TdJob(login_details, thread_title, topic_code, thread_reply, thread_job, nl_account, nl_account_pk, minutes)
                messages.success(request, "Activated Job!!!")
            except:
                messages.warning(request, "Request timed out, please try again!!!")

            return redirect(reverse('threadreplyjob-detail', kwargs={'pk':thread_job.pk}))
        
    return render(request, 'bot/theme/td_activate.html', {'nl_accounts':nl_accounts, 'thread_job':thread_job})


@login_required(login_url="/login/")
def deactivateTdJob(request, pk):
    thread_job = get_object_or_404(models.ThreadReplyJob, ('pk',pk))
    if request.method == 'POST':
        nl_account_pk = request.POST['nl_account_pk']
        nl_account = get_object_or_404(models.NairalandAccount, ('pk',nl_account_pk))
        #Check If Account has job
        if nl_account.has_job == True:
            nl_account.has_job = False
            thread_job.activated = False
            thread_job.nl_account_pk= None
            try:
                cron_jobs.scheduler.remove_job(nl_account_pk)
            except:
                pass
            nl_account.save()
            thread_job.save()

        return HttpResponseRedirect(reverse('threadreplyjob-detail', kwargs={'pk':thread_job.pk}))
        





@login_required(login_url="/login/")
def activateBjJob(request, pk):
    nl_accounts = models.NairalandAccount.objects.all()
    board_job = get_object_or_404(models.BoardReplyJob, ('pk',pk))
    board_uri = board_job.board_uri
    board_reply = board_job.reply


    if request.method == 'POST':
        nl_account_pk = request.POST['nl_account_pk']
        nl_account = get_object_or_404(models.NairalandAccount, ('pk',nl_account_pk))
        #Check If Account has job
        if nl_account.has_job == True:
            messages.warning(request, "NL Account has a job!!!")
        else:
            minutes = request.POST['minutes']
            login_details = {'name':nl_account.username,'password':nl_account.password}
            try:
                start_BjJob(login_details, board_uri, board_reply, board_job, nl_account, nl_account_pk, minutes)
                messages.success(request, "Activated Job!!!")
            except:
                messages.warning(request, "Request timed out, please try again!!!")

            return HttpResponseRedirect(reverse('boardreplyjob-detail', kwargs={'pk':board_job.pk}))
        

        
    return render(request, 'bot/theme/bj_activate.html', {'nl_accounts':nl_accounts, 'board_job':board_job})


@login_required(login_url="/login/")
def deactivateBjJob(request, pk):
    board_job = get_object_or_404(models.BoardReplyJob, ('pk',pk))
    if request.method == 'POST':
        nl_account_pk = request.POST['nl_account_pk']
        nl_account = get_object_or_404(models.NairalandAccount, ('pk',nl_account_pk))
        #Check If Account has job
        if nl_account.has_job == True:
            nl_account.has_job = False
            board_job.activated = False
            board_job.nl_account_pk= None
            try:
                cron_jobs.scheduler.remove_job(nl_account_pk)
            except:
                pass
            nl_account.save()
            board_job.save()

        return HttpResponseRedirect(reverse('boardreplyjob-detail', kwargs={'pk':board_job.pk}))
        


@login_required(login_url="/login/")
def activateFpJob(request, pk):
    nl_accounts = models.NairalandAccount.objects.all()
    frontpage_job = get_object_or_404(models.FrontPageMonitorJob, ('pk',pk))
    frontpage_reply = frontpage_job.reply


    if request.method == 'POST':
        nl_account_pk = request.POST['nl_account_pk']
        nl_account = get_object_or_404(models.NairalandAccount, ('pk',nl_account_pk))
        #Check If Account has job
        if nl_account.has_job == True:
            messages.warning(request, "NL Account has a job!!!")
        else:
            seconds = request.POST['seconds']
            print(nl_account_pk)
            login_details = {'name':nl_account.username,'password':nl_account.password}
            try:
                start_FpJob(login_details, frontpage_reply, frontpage_job, nl_account, nl_account_pk, seconds)
                messages.success(request, "Activated Job!!!")
            except:
                messages.warning(request, "Request timed out, please try again!!!")

            return HttpResponseRedirect(reverse('frontpagemonitorjob-detail', kwargs={'pk':frontpage_job.pk}))
        

        
    return render(request, 'bot/theme/fp_activate.html', {'nl_accounts':nl_accounts, 'frontpage_job':frontpage_job})


@login_required(login_url="/login/")
def deactivateFpJob(request, pk):
    frontpage_job = get_object_or_404(models.FrontPageMonitorJob, ('pk',pk))
    if request.method == 'POST':
        nl_account_pk = request.POST['nl_account_pk']
        nl_account = get_object_or_404(models.NairalandAccount, ('pk',nl_account_pk))
        #Check If Account has job
        if nl_account.has_job == True:
            nl_account.has_job = False
            frontpage_job.activated = False
            frontpage_job.nl_account_pk= None
            try:
                cron_jobs.scheduler.remove_job(nl_account_pk)
            except:
                pass
            nl_account.save()
            frontpage_job.save()

        return HttpResponseRedirect(reverse('frontpagemonitorjob-detail', kwargs={'pk':frontpage_job.pk}))
        




class NairalandAccountCreate(LoginRequiredMixin,CreateView):
    login_url = '/login'
    redirect_field_name = 'redirect_to'
    model = models.NairalandAccount
    template_name = 'bot/theme/account_form.html'
    fields = ['username', 'password']


class NairalandAccountDetail(LoginRequiredMixin, DetailView):
    login_url = '/login'
    redirect_field_name = 'redirect_to'
    model = models.NairalandAccount
    template_name = 'bot/theme/account_detail.html'


class NairalandAccountUpdate(LoginRequiredMixin, UpdateView):
    login_url = '/login'
    redirect_field_name = 'redirect_to'
    model = models.NairalandAccount
    template_name = 'bot/theme/account_update.html'
    fields = ['username','password']


class NairalandAccountDelete(LoginRequiredMixin, DeleteView):
    login_url = '/login'
    redirect_field_name = 'redirect_to'
    success_url = reverse_lazy('nairaland-accounts')
    model = models.NairalandAccount
    template_name = 'bot/theme/account_delete.html'







class BoardJobCreate(LoginRequiredMixin,CreateView):
    login_url = '/login'
    redirect_field_name = 'redirect_to'
    model = models.BoardReplyJob
    template_name = 'bot/theme/boardreplyjob_form.html'
    fields = ['board_name', 'board_uri', 'reply']

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        if user.profile.activated:
            pass
        else:
            messages.warning(request, "Please activate account!!!")
            return redirect('/license')
        return super(BoardJobCreate, self).dispatch(request, *args, **kwargs)


class BoardJobDetail(LoginRequiredMixin, DetailView):
    login_url = '/login'
    redirect_field_name = 'redirect_to'
    model = models.BoardReplyJob
    template_name = 'bot/theme/boardreplyjob_detail.html'


class BoardJobUpdate(LoginRequiredMixin, UpdateView):
    login_url = '/login'
    redirect_field_name = 'redirect_to'
    model = models.BoardReplyJob
    template_name = 'bot/theme/boardreplyjob_update.html'
    fields = ['board_name','board_uri', 'reply']


class BoardJobDelete(LoginRequiredMixin, DeleteView):
    login_url = '/login'
    redirect_field_name = 'redirect_to'
    success_url = reverse_lazy('jobs')
    model = models.BoardReplyJob
    template_name = 'bot/theme/boardreplyjob_delete.html'




class ThreadJobCreate(LoginRequiredMixin,CreateView):
    login_url = '/login'
    redirect_field_name = 'redirect_to'
    model = models.ThreadReplyJob
    template_name = 'bot/theme/threadreplyjob_form.html'
    fields = ['thread_title', 'topic_code', 'reply']

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        if user.profile.activated:
            pass
        else:
            messages.warning(request, "Please activate account!!!") 
            return redirect('/license')
        return super(ThreadJobCreate, self).dispatch(request, *args, **kwargs)




class ThreadJobDetail(LoginRequiredMixin, DetailView):
    login_url = '/login'
    redirect_field_name = 'redirect_to'
    model = models.ThreadReplyJob
    template_name = 'bot/theme/threadreplyjob_detail.html'


class ThreadJobUpdate(LoginRequiredMixin, UpdateView):
    login_url = '/login'
    redirect_field_name = 'redirect_to'
    model = models.ThreadReplyJob
    template_name = 'bot/theme/threadreplyjob_update.html'
    fields = ['thread_title', 'topic_code', 'reply']


class ThreadJobDelete(LoginRequiredMixin, DeleteView):
    login_url = '/login'
    redirect_field_name = 'redirect_to'
    success_url = reverse_lazy('jobs')
    model = models.ThreadReplyJob
    template_name = 'bot/theme/threadreplyjob_delete.html'




class FrontPageMonitorJobCreate(LoginRequiredMixin,CreateView):
    login_url = '/login'
    redirect_field_name = 'redirect_to'
    model = models.FrontPageMonitorJob
    template_name = 'bot/theme/frontpagemonitorjob_form.html'
    fields = ['reply',]


    def dispatch(self, request, *args, **kwargs):
        user = request.user
        if user.profile.activated and user.profile.account_type == 'pr':
            pass
        else:
            messages.warning(request, 'Only Premium Accounts can!!')
            return redirect('/jobs')
        return super(FrontPageMonitorJobCreate, self).dispatch(request, *args, **kwargs)




class FrontPageMonitorJobDetail(LoginRequiredMixin, DetailView):
    login_url = '/login'
    redirect_field_name = 'redirect_to'
    model = models.FrontPageMonitorJob
    template_name = 'bot/theme/frontpagemonitorjob_detail.html'


class FrontPageMonitorJobUpdate(LoginRequiredMixin, UpdateView):
    login_url = '/login'
    redirect_field_name = 'redirect_to'
    model = models.FrontPageMonitorJob
    template_name = 'bot/theme/frontpagemonitorjob_update.html'
    fields = [ 'reply',]


class FrontPageMonitorJobDelete(LoginRequiredMixin, DeleteView):
    login_url = '/login'
    redirect_field_name = 'redirect_to'
    success_url = reverse_lazy('jobs')
    model = models.FrontPageMonitorJob
    template_name = 'bot/theme/frontpagemonitorjob_delete.html'





