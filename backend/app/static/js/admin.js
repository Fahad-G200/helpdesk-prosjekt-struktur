document.getElementById('selectAll').addEventListener('change', function() {
  document.querySelectorAll('.ticketCheckbox').forEach(cb => cb.checked = this.checked);
});
