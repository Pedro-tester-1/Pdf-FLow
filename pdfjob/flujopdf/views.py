from django.shortcuts import render, redirect
from django.template.response import TemplateResponse
from django.contrib.auth.decorators import login_required
from django.contrib import auth, messages
from django.contrib.auth.models import User
from django.conf import settings
from django.http import JsonResponse, HttpResponse, Http404
from django.utils import timezone
from flujopdf.models import Job, Page, Version, Comentario
import os


def login_view(request):
    return TemplateResponse(request, 'login.html', {})


def register(request):
    return TemplateResponse(request, 'register.html', {})


@login_required(login_url='/pdfflow/login/')
def main(request):
    jobs = Job.objects.filter(deleted=False)
    return render(request, 'jobs.html', {'jobs': jobs})


def valida_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = auth.authenticate(request, username=username, password=password)
        if user is not None:
            auth.login(request, user)
            return redirect('/pdfflow/')
        else:
            messages.error(request, 'Credenciales incorrectas')
            return redirect('/pdfflow/login/')
    return redirect('/pdfflow/login/')


def crear_usuario(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email', '')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')

        if password != password2:
            messages.error(request, 'Las contraseñas no coinciden')
            return redirect('/pdfflow/register/')
        if User.objects.filter(username=username).exists():
            messages.error(request, 'El usuario ya existe')
            return redirect('/pdfflow/register/')
        if email and User.objects.filter(email=email).exists():
            messages.error(request, 'El email ya está registrado')
            return redirect('/pdfflow/register/')

        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()
        messages.success(request, 'Cuenta creada exitosamente. Inicia sesión.')
        return redirect('/pdfflow/login/')
    return redirect('/pdfflow/register/')


@login_required(login_url='/pdfflow/login/')
def pages(request, jobid):
    pages = Page.objects.filter(job_id=jobid)
    return render(request, 'pages.html', {'pages': pages})


def create_files(file, fileid):
    if not os.path.isfile(file):
        raise FileNotFoundError(f'Archivo no encontrado: {file}')

    rootpath = os.path.join(str(settings.BASE_DIR), 'data')
    svg_dir = os.path.join(rootpath, 'svg')
    thumb_dir = os.path.join(rootpath, 'thumb')
    os.makedirs(svg_dir, exist_ok=True)
    os.makedirs(thumb_dir, exist_ok=True)

    svgfile = os.path.join(svg_dir, str(fileid) + '.svg')
    ret = os.system('pdf2svg "{0}" "{1}"'.format(file, svgfile))
    if ret != 0 or not os.path.exists(svgfile):
        raise RuntimeError(f'pdf2svg falló (código {ret}) para {file}')

    from wand.image import Image
    thumb = Image(filename=file, resolution=72)
    thumb.resize(50, 50)
    thumb.save(filename=os.path.join(thumb_dir, str(fileid) + '.jpg'))
    thumb.close()


@login_required(login_url='/pdfflow/login/')
def load_jobs(request):
    if request.method != 'POST':
        return JsonResponse({'ok': False}, status=405)

    jobname = request.POST.get('jobname', '').strip()
    files = request.FILES.getlist('pdfs')

    if not jobname or not files:
        return JsonResponse({'ok': False, 'error': 'Nombre y archivos requeridos'}, status=400)

    job_dir = os.path.join(str(settings.BASE_DIR), 'data', 'in', jobname)
    os.makedirs(job_dir, exist_ok=True)
    new_job, created = Job.objects.get_or_create(name=jobname)

    for f in files:
        filepath = os.path.join(job_dir, f.name)
        with open(filepath, 'wb') as dest:
            for chunk in f.chunks():
                dest.write(chunk)
        page = Page.objects.create(name=f.name, job=new_job, user=request.user)
        try:
            create_files(filepath, page.id)
        except Exception as e:
            page.delete()
            return JsonResponse({'ok': False, 'error': str(e)}, status=500)

    return JsonResponse({'ok': True})


@login_required(login_url='/pdfflow/login/')
def add_pages_to_job(request):
    if request.method != 'POST':
        return JsonResponse({'ok': False}, status=405)

    jobid = request.POST.get('jobid')
    files = request.FILES.getlist('pdfs')

    if not jobid or not files:
        return JsonResponse({'ok': False, 'error': 'Job y archivos requeridos'}, status=400)

    try:
        job = Job.objects.get(id=jobid)
    except Job.DoesNotExist:
        return JsonResponse({'ok': False, 'error': 'Job no encontrado'}, status=404)

    job_dir = os.path.join(str(settings.BASE_DIR), 'data', 'in', job.name)
    os.makedirs(job_dir, exist_ok=True)

    for f in files:
        filepath = os.path.join(job_dir, f.name)
        with open(filepath, 'wb') as dest:
            for chunk in f.chunks():
                dest.write(chunk)
        page = Page.objects.create(name=f.name, job=job, user=request.user)
        try:
            create_files(filepath, page.id)
        except Exception as e:
            page.delete()
            return JsonResponse({'ok': False, 'error': str(e)}, status=500)

    return JsonResponse({'ok': True})


@login_required(login_url='/pdfflow/login/')
def page_svg(request, pageid):
    svg_path = os.path.join(str(settings.BASE_DIR), 'data', 'svg', str(pageid) + '.svg')
    if os.path.exists(svg_path):
        with open(svg_path, 'r') as f:
            content = f.read()
        return HttpResponse(content, content_type='image/svg+xml')
    raise Http404("SVG no encontrado")


@login_required(login_url='/pdfflow/login/')
def toggle_job_state(request):
    if request.method == 'POST':
        jobid = request.POST.get('jobid')
        try:
            job = Job.objects.get(id=jobid)
            job.state = 1 if job.state == 0 else 0
            job.closed = timezone.now() if job.state == 1 else None
            job.save()
            return JsonResponse({'ok': True, 'state': job.state})
        except Job.DoesNotExist:
            return JsonResponse({'ok': False}, status=404)
    return JsonResponse({'ok': False}, status=405)


@login_required(login_url='/pdfflow/login/')
def deletejob(request):
    if request.method == 'POST':
        jobid = request.POST.get('jobid')
        Job.objects.filter(id=jobid).update(deleted=True)
    return JsonResponse({})


@login_required(login_url='/pdfflow/login/')
def toggle_page_state(request):
    if request.method == 'POST':
        pageid = request.POST.get('pageid')
        state = request.POST.get('state')
        try:
            page = Page.objects.get(id=pageid)
            page.state = int(state)
            page.save()
            return JsonResponse({'ok': True, 'state': page.state})
        except Page.DoesNotExist:
            return JsonResponse({'ok': False}, status=404)
    return JsonResponse({'ok': False}, status=405)


@login_required(login_url='/pdfflow/login/')
def scan_input(request):
    if request.method != 'POST':
        return JsonResponse({'ok': False}, status=405)

    input_dir = os.path.join(str(settings.BASE_DIR), 'input')
    if not os.path.isdir(input_dir):
        return JsonResponse({'ok': False, 'error': f'Carpeta input no encontrada: {input_dir}'})

    created_jobs = 0
    created_pages = 0
    errors = []

    for folder_name in sorted(os.listdir(input_dir)):
        folder_path = os.path.join(input_dir, folder_name)
        if not os.path.isdir(folder_path):
            continue

        job, _ = Job.objects.get_or_create(name=folder_name)

        for filename in sorted(os.listdir(folder_path)):
            if not filename.lower().endswith('.pdf'):
                continue
            if Page.objects.filter(name=filename, job=job).exists():
                continue

            filepath = os.path.join(folder_path, filename)
            page = Page.objects.create(name=filename, job=job, user=request.user)
            try:
                create_files(filepath, page.id)
                created_pages += 1
            except Exception as e:
                page.delete()
                errors.append(f'{folder_name}/{filename}: {str(e)}')

        created_jobs += 1

    return JsonResponse({'ok': True, 'jobs': created_jobs, 'pages': created_pages, 'errors': errors})


@login_required(login_url='/pdfflow/login/')
def versions(request):
    vers = Version.objects.all().order_by('-date')
    return render(request, 'versions.html', {'versions': vers})


@login_required(login_url='/pdfflow/login/')
def create_version(request):
    if not request.user.is_staff:
        return JsonResponse({'ok': False, 'error': 'Sin permisos'}, status=403)
    if request.method == 'POST':
        tag = request.POST.get('tag', '').strip()
        description = request.POST.get('description', '').strip()
        if not tag:
            return JsonResponse({'ok': False, 'error': 'Tag requerido'}, status=400)
        if Version.objects.filter(tag=tag).exists():
            return JsonResponse({'ok': False, 'error': 'Ya existe esa versión'}, status=400)
        v = Version.objects.create(tag=tag, description=description, user=request.user)
        return JsonResponse({'ok': True, 'id': v.id, 'tag': v.tag, 'description': v.description})
    return JsonResponse({'ok': False}, status=405)


@login_required(login_url='/pdfflow/login/')
def delete_version(request):
    if not request.user.is_staff:
        return JsonResponse({'ok': False, 'error': 'Sin permisos'}, status=403)
    if request.method == 'POST':
        versionid = request.POST.get('versionid')
        Version.objects.filter(id=versionid).delete()
        return JsonResponse({'ok': True})
    return JsonResponse({'ok': False}, status=405)


@login_required(login_url='/pdfflow/login/')
def version_detail(request, versionid):
    try:
        version = Version.objects.get(id=versionid)
    except Version.DoesNotExist:
        raise Http404
    comentarios = version.comentarios.all().order_by('date')
    return JsonResponse({
        'id': version.id,
        'tag': version.tag,
        'description': version.description,
        'comentarios': [{'id': c.id, 'texto': c.texto, 'user': str(c.user), 'date': c.date.strftime('%b %d, %Y')} for c in comentarios]
    })


@login_required(login_url='/pdfflow/login/')
def add_comentario(request):
    if request.method == 'POST':
        versionid = request.POST.get('versionid')
        texto = request.POST.get('texto', '').strip()
        if not texto:
            return JsonResponse({'ok': False, 'error': 'Comentario vacío'}, status=400)
        try:
            version = Version.objects.get(id=versionid)
        except Version.DoesNotExist:
            return JsonResponse({'ok': False, 'error': 'Versión no encontrada'}, status=404)
        c = Comentario.objects.create(version=version, user=request.user, texto=texto)
        return JsonResponse({'ok': True, 'id': c.id, 'texto': c.texto, 'user': str(request.user), 'date': c.date.strftime('%b %d, %Y')})
    return JsonResponse({'ok': False}, status=405)
