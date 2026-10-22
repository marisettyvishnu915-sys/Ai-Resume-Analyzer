const navToggle = document.querySelector('.mobile-nav-toggle');
const header = document.querySelector('.site-header');

if (navToggle && header) {
  navToggle.addEventListener('click', () => {
    header.classList.toggle('nav-open');
  });
}

const observer = new IntersectionObserver((entries) => {
  entries.forEach((entry) => {
    if (entry.isIntersecting) {
      const target = entry.target;
      const value = Number(target.getAttribute('data-target'));
      const suffix = target.textContent.includes('m') ? 'm' : '%';

      if (target.dataset.done) return;

      let start = 0;
      const duration = 1200;
      const step = Math.round(value / (duration / 16));

      const interval = setInterval(() => {
        start += step;
        if (start >= value) {
          target.textContent = value + (suffix === '%' ? '%' : 'm');
          target.dataset.done = 'true';
          clearInterval(interval);
        } else {
          target.textContent = start + (suffix === '%' ? '%' : 'm');
        }
      }, 16);
    }
  });
}, { threshold: 0.4 });

document.querySelectorAll('[data-target]').forEach((item) => observer.observe(item));

const gauge = document.querySelector('.score-gauge');

if (gauge) {
  const gaugeScore = Number(gauge.getAttribute('data-score')) || 87;
  const gaugeFront = document.querySelector('.gauge-front');
  const circleLength = 2 * Math.PI * 68;

  if (gaugeFront) {
    gaugeFront.style.strokeDasharray = circleLength;
    gaugeFront.style.strokeDashoffset = circleLength - (circleLength * gaugeScore / 100);
  }
}

const resumeForm = document.getElementById('resumeForm');
const resumeFile = document.getElementById('resumeFile');
const fileName = document.getElementById('fileName');
const resultStatus = document.getElementById('resultStatus');
const resultFile = document.getElementById('resultFile');
const jobDescription = document.getElementById('jobDescription');
const atsScore = document.getElementById('atsScore');
const jobMatchScore = document.getElementById('jobMatchScore');
const overallScore = document.getElementById('overallScore');
const missingSkills = document.getElementById('missingSkills');
const recommendedKeywords = document.getElementById('recommendedKeywords');

if (resumeFile && fileName) {
  resumeFile.addEventListener('change', () => {
    if (resumeFile.files && resumeFile.files.length > 0) {
      fileName.textContent = resumeFile.files[0].name;
      resultFile.textContent = resumeFile.files[0].name;
    }
  });
}

if (resumeForm) {
  resumeForm.addEventListener('submit', async (event) => {
    event.preventDefault();

    if (!resumeFile.files || resumeFile.files.length === 0) {
      resultStatus.textContent = 'Missing file';
      fileName.textContent = 'Choose a PDF or DOCX resume';
      return;
    }

    if (!jobDescription.value.trim()) {
      resultStatus.textContent = 'Add job text';
      return;
    }

    const formData = new FormData(resumeForm);
    resultStatus.textContent = 'Analyzing';
    resultFile.textContent = resumeFile.files[0].name;

    try {
      const response = await fetch('/analyze', {
        method: 'POST',
        body: formData
      });

      const payload = await response.json();
      if (!response.ok || !payload.ok) {
        resultStatus.textContent = payload.error || 'Upload failed';
        return;
      }

      resultStatus.textContent = 'Complete';
      resultFile.textContent = payload.file;
      fileName.textContent = payload.fileType + ' resume selected';

      if (atsScore) atsScore.textContent = payload.atsScore + '%';
      if (jobMatchScore) jobMatchScore.textContent = payload.jobMatchScore + '%';
      if (overallScore) overallScore.textContent = payload.overallScore + '/100';
      if (missingSkills) missingSkills.textContent = (payload.missingSkills || []).slice(0, 3).join(', ');
      if (recommendedKeywords) recommendedKeywords.textContent = (payload.recommendedKeywords || []).slice(0, 3).join(', ');
    } catch (err) {
      resultStatus.textContent = 'Error';
      resultFile.textContent = 'Upload failed';
      console.error(err);
    }
  });
}

if (resumeForm && document.getElementById('clearBtn')) {
  document.getElementById('clearBtn').addEventListener('click', () => {
    if (resumeFile) resumeFile.value = '';
    if (jobDescription) jobDescription.value = '';
    if (fileName) fileName.textContent = 'Choose a PDF or DOCX resume';
    if (resultFile) resultFile.textContent = 'No file selected';
    if (resultStatus) resultStatus.textContent = 'Ready';
    if (atsScore) atsScore.textContent = '--';
    if (jobMatchScore) jobMatchScore.textContent = '--';
    if (overallScore) overallScore.textContent = '--';
    if (missingSkills) missingSkills.textContent = 'No gaps yet';
    if (recommendedKeywords) recommendedKeywords.textContent = 'None';
  });
}
