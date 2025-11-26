from flask import Flask, render_template, request, session, redirect, url_for, flash, jsonify
from werkzeug.utils import secure_filename
import os
import uuid
from core.cv_parser import parse_cv
from core.scrapers import scrape_jobs
from core.matcher import MatchScoreEngine
from config import Config
from flask_session import Session

JOBS_CACHE = {}

def create_app():
    app = Flask(__name__, template_folder='templates', static_folder='static')
    app.config.from_object(Config)
    Session(app)
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    matcher = MatchScoreEngine()

    @app.before_request
    def reload_users():
        from core.auth import reload_users_db
        reload_users_db()

    @app.route('/')
    def landing():
        return render_template('landing.html')

    @app.route('/search', methods=['GET', 'POST'])
    def search():
        jobs = []
        search_performed = False
        role = ""
        place = ""

        if request.method == 'POST':
            role = request.form.get('role', '').strip()
            place = request.form.get('place', '').strip()

            if role:
                flash(f"Searching for '{role}'...", "info")
                try:
                    scraped_jobs = scrape_jobs(role, place)
                    search_performed = True
                    
                    jobs = []
                    for job in scraped_jobs:
                        job_id = str(uuid.uuid4())
                        job['id'] = job_id
                        JOBS_CACHE[job_id] = job
                        jobs.append(job)

                    if not jobs:
                        flash("No jobs found. Try 'python developer' or 'data analyst'.", "warning")
                except Exception as e:
                    flash("Scraping error. Try again.", "error")
                    print(f"Error: {e}")

        if session.get('cv_parsed') and jobs:
            cv_data = session['cv_parsed']
            for job in jobs:
                score, missing = matcher.calculate_score(job, cv_data)
                job['match_score'] = score
                job['missing_skills'] = missing

        return render_template('results.html', jobs=jobs, search_performed=search_performed)

    @app.route('/job/<job_id>')
    def job_detail(job_id):
        job = JOBS_CACHE.get(job_id)
        if not job:
            flash('Job not found or expired', 'error')
            return redirect('/search')
        return render_template('job_detail.html', job=job)

    @app.route('/upload', methods=['GET', 'POST'])
    def upload_cv():
        from core.auth import is_logged_in, get_current_user, USERS_DB, _save_users
        
        if request.method == 'POST':
            if 'cv_file' not in request.files:
                flash('No file selected', 'error')
                return redirect(request.url)

            file = request.files['cv_file']
            if file.filename == '':
                flash('No file selected', 'error')
                return redirect(request.url)

            if not file.filename.lower().endswith(('.pdf', '.docx')):
                flash('Only PDF & DOCX allowed', 'error')
                return redirect(request.url)

            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            try:
                cv_data = parse_cv(filepath)
                session['cv_parsed'] = cv_data
                session['cv_filename'] = filename
                
                if is_logged_in():
                    user = get_current_user()
                    if user:
                        user.cv_data = cv_data
                        user.cv_filename = filename
                        _save_users(USERS_DB)
                
                flash(f"CV '{filename}' analyzed successfully!", 'success')
            except Exception as e:
                flash('Error reading CV', 'error')
                print(f"CV Parse Error: {e}")

            return redirect('/search')

        return render_template('upload.html')

    @app.route('/save-job/<job_id>')
    def save_job(job_id):
        from core.user import User
        user = User()
        action = user.toggle_saved_job(job_id)
        flash(f"Job {action} to saved list.", "success")
        return redirect(request.referrer or '/search')

    @app.route('/saved-jobs')
    def saved_jobs():
        from core.user import User
        user = User()
        saved_ids = user.data['saved_jobs']
        saved_jobs_list = [JOBS_CACHE[jid] for jid in saved_ids if jid in JOBS_CACHE]
        return render_template('results.html', jobs=saved_jobs_list, search_performed=True, title="Saved Jobs")

    @app.route('/build-cv')
    def build_cv():
        return render_template('build_cv.html')

    @app.route('/bot/chat', methods=['POST'])
    def bot_chat():
        from core.bot import JobBot
        data = request.json
        action = data.get('action')
        context = data.get('context', {})
        
        bot = JobBot()
        response = bot.generate_response(action, context)
        
        return {"response": response}

    @app.route('/remove-cv')
    def remove_cv():
        session.pop('cv_parsed', None)
        session.pop('cv_filename', None)
        flash('CV removed', 'info')
        return redirect('/search')

    @app.route('/signin', methods=['GET', 'POST'])
    def signin():
        from core.auth import login_user
        if request.method == 'POST':
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '')
            
            user, error = login_user(username, password)
            if user:
                session['user_id'] = user.id
                session['username'] = user.username
                flash(f'Welcome back, {user.username}!', 'success')
                return redirect('/')
            else:
                flash(error, 'error')
        
        return render_template('signin.html')

    @app.route('/signup', methods=['GET', 'POST'])
    def signup():
        from core.auth import register_user
        if request.method == 'POST':
            username = request.form.get('username', '').strip()
            email = request.form.get('email', '').strip()
            password = request.form.get('password', '')
            
            user, error = register_user(username, email, password)
            if user:
                session['user_id'] = user.id
                session['username'] = user.username
                flash(f'Account created! Welcome, {user.username}!', 'success')
                return redirect('/')
            else:
                flash(error, 'error')
        
        return render_template('signup.html')

    @app.route('/logout')
    def logout():
        from core.auth import logout_user
        logout_user()
        flash('Logged out successfully', 'info')
        return redirect('/')

    @app.route('/profile')
    def profile():
        from core.auth import is_logged_in, get_current_user
        if not is_logged_in():
            flash('Please sign in to view your profile', 'warning')
            return redirect('/signin')
        
        user = get_current_user()
        if not user:
            flash('User session expired. Please sign in again.', 'warning')
            return redirect('/signin')
            
        return render_template('profile.html', user=user)

    @app.route('/chat', methods=['GET'])
    def chat_page():
        from core.auth import is_logged_in, get_current_user
        if not is_logged_in():
            flash('Please sign in to use the Chat Bot', 'warning')
            return redirect('/signin')
        
        user = get_current_user()
        if not user:
            flash('User session expired. Please sign in again.', 'warning')
            return redirect('/signin')
            
        return render_template('chat.html', user=user)

    @app.route('/chat/send', methods=['POST'])
    def chat_send():
        from core.auth import is_logged_in, get_current_user
        
        if not is_logged_in():
            return jsonify({'error': 'Not authenticated'}), 401
        
        user = get_current_user()
        if not user:
            return jsonify({'error': 'User not found'}), 404
            
        data = request.json
        message = data.get('message', '')
        
        if 'chat_history' not in session:
            session['chat_history'] = []
        
        try:
            from core.rag_chat import RAGChatBot
            bot = RAGChatBot(user.cv_data if user.cv_data else {})
            
            response = bot.generate_response(message, session['chat_history'])
            
            session['chat_history'].append({
                'user': message,
                'assistant': response
            })
            
            if len(session['chat_history']) > 10:
                session['chat_history'] = session['chat_history'][-10:]
            
            session.modified = True
            
        except Exception as e:
            print(f"RAG Chat error: {e}")
            import traceback
            traceback.print_exc()
            response = "Chat bot is being set up. Please check back soon!"
        
        return jsonify({'response': response})

    return app

app = create_app()

if __name__ == '__main__':
    print("JobFinder AI is LIVE -> http://127.0.0.1:5000")
    app.run(host='127.0.0.1', port=5000, debug=True, threaded=True)        
