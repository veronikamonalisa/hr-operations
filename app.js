const sections = ['dashboard', 'employees', 'leave', 'payroll', 'recruitment', 'performance'];
const titles = {
  dashboard: 'Dashboard',
  employees: 'Employee Directory',
  leave: 'Leave Management',
  payroll: 'Payroll',
  recruitment: 'Recruitment',
  performance: 'Performance Reviews'
};

function showSection(name) {
  // Hide all sections
  sections.forEach(s => {
    document.getElementById('section-' + s)?.classList.remove('active');
  });

  // Show selected section
  document.getElementById('section-' + name)?.classList.add('active');

  // Update header title
  document.getElementById('page-title').textContent = titles[name] || name;

  // Update nav active state
  document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));
  event.currentTarget.classList.add('active');
}
