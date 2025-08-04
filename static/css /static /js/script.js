document.addEventListener('DOMContentLoaded', function() {
  // File selection feedback
  document.querySelectorAll('.upload-btn input').forEach(input => {
    input.addEventListener('change', function() {
      if(this.files.length > 0) {
        const label = this.closest('.upload-btn');
        label.querySelector('.upload-icon').textContent = '✓';
        label.querySelector('.upload-icon').style.color = '#4CAF50';
      }
    });
  });
});
