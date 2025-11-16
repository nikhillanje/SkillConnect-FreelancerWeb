document.addEventListener('DOMContentLoaded', () => {
    const clientCard = document.getElementById('client-card');
    const freelancerCard = document.getElementById('freelancer-card');
    const applyButton = document.getElementById('apply-button');

    let selectedRole = null;

    const selectCard = (role) => {
        selectedRole = role;

        if (role === 'client') {
            clientCard.classList.add('selected');
            freelancerCard.classList.remove('selected');
            applyButton.textContent = 'Continue as Client';
        } else {
            freelancerCard.classList.add('selected');
            clientCard.classList.remove('selected');
            applyButton.textContent = 'Continue as Freelancer';
        }

        applyButton.disabled = false;
        applyButton.classList.remove('disabled-button');
        console.log("Role Selected:", role);
    };

    clientCard.addEventListener('click', () => selectCard('client'));
    freelancerCard.addEventListener('click', () => selectCard('freelancer'));

    applyButton.addEventListener('click', () => {
        if (!selectedRole) return;
        window.location.href = selectedRole === 'client'
            ? '/client_Signup/'
            : '/freelancer_Signup/';
    });
});
