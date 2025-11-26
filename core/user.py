from flask import session

class User:
    def __init__(self):
        self.data = session.get('user_profile', {
            "saved_jobs": [],
            "history": [],
            "preferences": {}
        })

    def save(self):
        session['user_profile'] = self.data
        session.modified = True

    def toggle_saved_job(self, job_id):
        if job_id in self.data['saved_jobs']:
            self.data['saved_jobs'].remove(job_id)
            action = "removed"
        else:
            self.data['saved_jobs'].append(job_id)
            action = "added"
        self.save()
        return action

    def is_job_saved(self, job_id):
        return job_id in self.data['saved_jobs']

    def add_history(self, search_term):
        if search_term not in self.data['history']:
            self.data['history'].insert(0, search_term)
            self.data['history'] = self.data['history'][:10]
            self.save()

    def get_saved_jobs_count(self):
        return len(self.data['saved_jobs'])
