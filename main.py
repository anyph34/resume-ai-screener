from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import init_db, get_db
from models import Job, Resume, Match
from resume_parser import parse_resume
from job_analyzer import analyze_job_description
from matcher import calculate_match_score

app = FastAPI(title="AI Resume Screener")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class JobCreate(BaseModel):
    title: str
    description: str

@app.on_event("startup")
def startup():
    init_db()

@app.get("/", response_class=HTMLResponse)
def frontend():
    return """
    <!DOCTYPE html>
    <html>
    <head><title>AI Resume Screener</title><style>
        body{font-family:Arial;margin:40px;background:#f5f5f5;}
        .container{max-width:800px;margin:auto;background:white;padding:20px;border-radius:10px;}
        input,textarea,button{width:100%;padding:10px;margin:10px 0;}
        button{background:#007bff;color:white;border:none;cursor:pointer;border-radius:5px;}
        .result{background:#e9ecef;padding:10px;margin:10px 0;border-radius:5px;}
    </style></head>
    <body><div class=container>
        <h1>🤖 AI Resume Screening System</h1>
        <h2>1. Create Job</h2>
        <input type=text id=jobTitle placeholder="Job Title">
        <textarea id=jobDesc rows=5 placeholder="Job Description"></textarea>
        <button onclick="createJob()">Create Job</button>
        <h2>2. Upload Resume</h2>
        <input type=file id=resumeFile accept=".pdf,.docx">
        <button onclick="uploadResume()">Upload Resume</button>
        <h2>3. Match</h2>
        <input type=number id=jobId placeholder="Job ID">
        <input type=number id=resumeId placeholder="Resume ID">
        <button onclick="matchResume()">Match</button>
        <h2>4. All Matches</h2>
        <button onclick="viewMatches()">Show Matches</button>
        <div id=results></div>
    </div>
    <script>
        async function createJob(){
            const title=document.getElementById('jobTitle').value;
            const desc=document.getElementById('jobDesc').value;
            const res=await fetch('/api/jobs',{
                method:'POST',
                headers:{'Content-Type':'application/json'},
                body:JSON.stringify({title:title,description:desc})
            });
            const data=await res.json();
            alert('Job created ID: '+data.id);
        }
        async function uploadResume(){
            const fd=new FormData();
            const fileInput=document.getElementById('resumeFile');
            fd.append('file',fileInput.files[0]);
            const res=await fetch('/api/resumes',{method:'POST',body:fd});
            const data=await res.json();
            alert('Resume uploaded ID: '+data.id);
        }
        async function matchResume(){
            const jobId=document.getElementById('jobId').value;
            const resumeId=document.getElementById('resumeId').value;
            const res=await fetch(`/api/match/${jobId}/${resumeId}`);
            const data=await res.json();
            const resultsDiv=document.getElementById('results');
            resultsDiv.innerHTML='<div class=result><pre>'+JSON.stringify(data,null,2)+'</pre></div>';
        }
        async function viewMatches(){
            const res=await fetch('/api/matches');
            const data=await res.json();
            const resultsDiv=document.getElementById('results');
            resultsDiv.innerHTML='<div class=result><pre>'+JSON.stringify(data,null,2)+'</pre></div>';
        }
    </script>
    </body></html>
    """

@app.post("/api/jobs")
def create_job(job: JobCreate, db: Session = Depends(get_db)):
    analysis = analyze_job_description(job.description)
    new_job = Job(
        title=job.title,
        description=job.description,
        required_skills=",".join(analysis["required_skills"]),
        min_experience_years=analysis["min_experience_years"]
    )
    db.add(new_job)
    db.commit()
    db.refresh(new_job)
    return {"id": new_job.id}

@app.post("/api/resumes")
async def upload_resume(file: UploadFile = File(...), db: Session = Depends(get_db)):
    parsed = await parse_resume(file)
    resume = Resume(
        filename=parsed["filename"],
        extracted_text=parsed["extracted_text"],
        email=parsed["email"],
        word_count=parsed["word_count"]
    )
    db.add(resume)
    db.commit()
    db.refresh(resume)
    return {"id": resume.id}

@app.get("/api/match/{job_id}/{resume_id}")
def match_resume(job_id: int, resume_id: int, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not job or not resume:
        raise HTTPException(status_code=404, detail="Job or Resume not found")
    
    skills = job.required_skills.split(",") if job.required_skills else []
    result = calculate_match_score(resume.extracted_text, job.description, skills)
    
    match = Match(job_id=job_id, resume_id=resume_id, similarity_score=result["similarity_score"])
    db.add(match)
    db.commit()
    return result

@app.get("/api/matches")
def get_matches(db: Session = Depends(get_db)):
    return db.query(Match).all()
