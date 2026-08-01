let chart;

function getTopItems(list, max = 15) {
    return list.slice(0, max);
}

document.getElementById('resumeFile').addEventListener('change', function() {
    const fileLabel = document.getElementById('fileUploadText');
    const resumeText = document.getElementById('resumeText');
    if (this.files && this.files.length > 0) {
        fileLabel.textContent = "📄 " + this.files[0].name + " (Uploaded)";
        fileLabel.style.color = "#34d399";
        fileLabel.style.borderColor = "#34d399";
        resumeText.disabled = true;
        resumeText.value = "";
        resumeText.placeholder = "File uploaded. Manual text entry disabled.";
    } else {
        fileLabel.textContent = "Upload File (.pdf, .docx)";
        fileLabel.style.color = "";
        fileLabel.style.borderColor = "";
        resumeText.disabled = false;
        resumeText.placeholder = "Paste the candidate's resume here...";
    }
});

document.getElementById('screenForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const analyzeBtn = document.getElementById('analyzeBtn');
    const OriginalBtnText = analyzeBtn.innerHTML;
    analyzeBtn.innerHTML = 'Analyzing...';
    analyzeBtn.disabled = true;

    const formData = new FormData();
    formData.append('resume_text', document.getElementById('resumeText').value);

    const resumeFile = document.getElementById('resumeFile');
    if (resumeFile.files[0]) {
        formData.append('resume_file', resumeFile.files[0]);
    }

    formData.append('jd_text', document.getElementById('jdText').value);
    formData.append('jd_exp', document.getElementById('jdExp').value || 0);

    try {
        const res = await fetch('/analyze', { method: 'POST', body: formData });
        const data = await res.json();

        if (data.error) {
            alert(data.error);
            return;
        }

        // Show Results
        const resultsPanel = document.getElementById('results');
        resultsPanel.classList.remove('hidden');

        // Animate entrance
        resultsPanel.animate([
            { opacity: 0, transform: 'translateY(20px)' },
            { opacity: 1, transform: 'translateY(0)' }
        ], { duration: 600, easing: 'ease-out' });

        // Populate Scores
        document.getElementById('finalScore').textContent = data.final_score.toFixed(2) + "%";
        document.getElementById('contentScore').textContent = data.content_match.toFixed(2) + "%";
        document.getElementById('skillScore').textContent = data.skill_match.toFixed(2) + "%";
        
        const jdExpVal = document.getElementById('jdExp').value;
        document.getElementById('expScore').textContent = (!jdExpVal || jdExpVal == 0) ? "N/A" : data.experience_match.toFixed(2) + "%";

        // Progress Bars
        document.getElementById('finalBar').style.width = data.final_score.toFixed(2) + "%";
        document.getElementById('skillBar').style.width = data.skill_match.toFixed(2) + "%";
        
        document.getElementById('finalScoreText').textContent = data.final_score.toFixed(2) + "%";
        document.getElementById('skillScoreText').textContent = data.skill_match.toFixed(2) + "%";

        // Lists
        const createTags = (arr, className = '') => arr.length ? arr.map(s => `<li class="${className}">${s}</li>`).join('') : '<li>None</li>';

        document.getElementById('matchedSkills').innerHTML = createTags(data.matched_skills, 'bg-dark text-white');
        document.getElementById('missingSkills').innerHTML = createTags(data.skill_gaps, 'bg-danger text-white');
        
        // Show result paneltails
        if (data.candidate_profile) {
            document.getElementById('candName').textContent = data.candidate_profile.name !== "Not Found" ? data.candidate_profile.name : "Candidate Identity Extracted";
            document.getElementById('candEmail').textContent = data.candidate_profile.email || "Not Found";
            document.getElementById('candPhone').textContent = data.candidate_profile.phone || "Not Found";
            
            const edu = getTopItems(data.candidate_profile.education || [], 4);
            document.getElementById('candEdu').innerHTML = createTags(edu);
        }

        // Chart with exact new Theme Colors
        if (chart) chart.destroy();

        Chart.defaults.color = "#94a3b8";
        Chart.defaults.font.family = "'Outfit', sans-serif";

        const ctx = document.getElementById('chart').getContext('2d');
        
        const gradient1 = ctx.createLinearGradient(0, 0, 0, 200);
        gradient1.addColorStop(0, '#6366f1'); // Indigo
        gradient1.addColorStop(1, '#a855f7'); // Purple
        
        const gradient2 = ctx.createLinearGradient(0, 0, 0, 200);
        gradient2.addColorStop(0, '#10b981'); // Emerald
        gradient2.addColorStop(1, '#3b82f6'); // Blue
        
        const gradient3 = ctx.createLinearGradient(0, 0, 0, 200);
        gradient3.addColorStop(0, '#f43f5e'); // Rose
        gradient3.addColorStop(1, '#f97316'); // Orange

        chart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Semantic', 'Skills', 'Experience'],
                datasets: [{
                    data: [
                        data.semantic_similarity,
                        data.skill_match,
                        data.experience_match
                    ],
                    backgroundColor: [gradient1, gradient2, gradient3],
                    borderWidth: 0,
                    hoverOffset: 10
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: '75%',
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 15,
                            usePointStyle: true,
                            pointStyle: 'circle'
                        }
                    }
                },
                animation: {
                    animateScale: true,
                    animateRotate: true
                }
            }
        });
        
        // Scroll to results on mobile
        if(window.innerWidth <= 900) {
            resultsPanel.scrollIntoView({ behavior: 'smooth' });
        }

    } catch (err) {
        console.error(err);
        alert("Failed to analyze. Please try again.");
    } finally {
        analyzeBtn.innerHTML = OriginalBtnText;
        analyzeBtn.disabled = false;
    }
});