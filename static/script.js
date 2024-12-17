document.addEventListener("DOMContentLoaded", function() {
    const isTicketViewer = window.location.pathname.endsWith('ticket-viewer.html');

    async function loadDatabase() {
        try {
            const response = await fetch('/database.json');
            const data = await response.json();
            console.log('Database loaded:', data); 
            return data;
        } catch (error) {
            console.error('Error loading database:', error);
            return null;
        }
    }

    function displayTicketList(tickets) {
        const ticketList = document.getElementById('ticket-list');
        if (!ticketList) {
            console.error('Ticket list container not found');
            return;
        }

        ticketList.innerHTML = ''; 

        tickets.forEach(ticket => {
            const ticketElement = document.createElement('div');
            ticketElement.classList.add('ticket-item');
            
            const ticketNum = ticket.ticket_number || 'Unknown';
            const messageCount = ticket.messages?.length || 0;
            const creatorInfo = ticket.creator ? 
                `Created by ${ticket.creator.name}` : 
                'No creator info';
            
            ticketElement.innerHTML = `
                <span>Ticket #${ticketNum} (${messageCount} messages)</span>
                <span class="creator-info">${creatorInfo}</span>
            `;
            
            ticketElement.onclick = () => {
                window.location.href = `ticket-viewer.html?ticket=${ticketNum}`;
            };
            ticketList.appendChild(ticketElement);
        });

        if (ticketList.innerHTML === '') {
            ticketList.innerHTML = 'No tickets found.';
        }
    }

    function displayTicketMessages(ticket) {
        const transcriptContainer = document.getElementById('transcript-container');
        if (!transcriptContainer) {
            console.error('Transcript container not found');
            return;
        }

        
        const ticketNumber = document.getElementById('ticket-number');
        const creatorName = document.getElementById('creator-name');
        const createdAt = document.getElementById('created-at');
        const creatorAvatar = document.getElementById('creator-avatar');

        const ticketNum = ticket.ticket_number || 'Unknown';
        const messageCount = ticket.messages?.length || 0;

        
        if (ticketNumber) {
            ticketNumber.textContent = `Ticket #${ticketNum} (${messageCount} messages)`;
        }

        
        if (ticket.creator) {
            if (creatorName) {
                creatorName.textContent = `Created by: ${ticket.creator.name}`;
            }
            if (createdAt) {
                createdAt.textContent = `Created at: ${ticket.created_at || 'Unknown'}`;
            }
            if (creatorAvatar) {
                creatorAvatar.src = ticket.creator.avatar_url || '/static/default_avatar.png';
            }
        }
        
        transcriptContainer.innerHTML = '';
        const messagesContainer = document.createElement('div');
        messagesContainer.classList.add('messages-container');

        if (!ticket.messages || ticket.messages.length === 0) {
            messagesContainer.innerHTML = '<div class="message">No messages in this ticket.</div>';
        } else {
            ticket.messages.forEach(message => {
                const messageElement = document.createElement('div');
                messageElement.classList.add('message');

                const messageHeader = document.createElement('div');
                messageHeader.classList.add('message-header');

                const usernameElement = document.createElement('span');
                usernameElement.classList.add('username');
                usernameElement.textContent = message.author;

                const timestampElement = document.createElement('span');
                timestampElement.classList.add('timestamp');
                timestampElement.textContent = message.timestamp;

                messageHeader.appendChild(usernameElement);
                messageHeader.appendChild(timestampElement);

                const contentElement = document.createElement('div');
                contentElement.classList.add('content');
                contentElement.textContent = message.content;

                messageElement.appendChild(messageHeader);
                messageElement.appendChild(contentElement);

                messagesContainer.appendChild(messageElement);
            });
        }
        
        transcriptContainer.appendChild(messagesContainer);

        
        transcriptContainer.scrollTop = transcriptContainer.scrollHeight;
    }

    loadDatabase().then(data => {
        if (!data || !data.tickets) {
            console.error('No ticket data found');
            return;
        }

        if (isTicketViewer) {
            const urlParams = new URLSearchParams(window.location.search);
            const ticketNumber = urlParams.get('ticket');
            console.log('Viewing ticket number:', ticketNumber);
            const ticket = data.tickets.find(t => t.ticket_number === ticketNumber || t.ticket_number === parseInt(ticketNumber));
            if (ticket) {
                displayTicketMessages(ticket);
            } else {
                document.getElementById('transcript-container').innerHTML = 
                    '<div class="message">Ticket not found.</div>';
            }
        } else {
            displayTicketList(data.tickets);
        }
    });
});
