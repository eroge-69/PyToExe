import webview
import os

# Define the HTML content from your Quantum-27.html file
# This string contains the entire HTML structure, including CSS and JavaScript.
# We're loading it directly here, but in a larger app, you might read it from an index.html file.
# For simplicity, and to ensure the HTML is self-contained in this response,
# I am embedding it directly as a multi-line string.
html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Quantum Business Activity Dashboard</title>
  <!-- Tailwind CSS CDN -->
  <script src="https://cdn.tailwindcss.com"></script>
  <!-- Inter Font -->
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
  <!-- XLSX library for Excel export -->
  <script src="https://cdnjs.cloudflare.com/ajax/libs/xlsx/0.18.5/xlsx.full.min.js"></script>
  <!-- jsPDF library for PDF export -->
  <script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js"></script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf-autotable/3.5.14/jspdf.plugin.autotable.min.js"></script>
  <style>
    body {
      font-family: 'Inter', sans-serif;
    }
    /* Custom styles for the message box and modals */
    .modal-overlay {
      position: fixed;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      background: rgba(0, 0, 0, 0.6);
      display: flex;
      justify-content: center;
      align-items: center;
      z-index: 1000;
      transition: opacity 0.3s ease-in-out;
      opacity: 0;
      pointer-events: none;
    }
    .modal-overlay.active {
      opacity: 1;
      pointer-events: auto;
    }
    .modal-content {
      background: white;
      padding: 24px;
      border-radius: 8px;
      box-shadow: 0 8px 24px rgba(0, 0, 0, 0.25);
      max-width: 90%;
      max-height: 90%; /* Limit height to prevent overflow on small screens */
      overflow-y: auto; /* Enable scrolling for modal content */
      position: relative;
      transform: translateY(-20px);
      transition: transform 0.3s ease-in-out;
    }
    .modal-overlay.active .modal-content {
      transform: translateY(0);
    }
    .message-box {
      text-align: center;
      max-width: 400px;
      width: 90%;
    }
    .message-box h3 {
      font-size: 1.25rem;
      font-weight: 600;
      margin-bottom: 16px;
      color: #333;
    }
    .message-box p {
      margin-bottom: 24px;
      color: #555;
    }
    .message-box button {
      background-color: #EF4444; /* Red-500 */
      color: white;
      padding: 10px 20px;
      border-radius: 6px;
      transition: background-color 0.2s ease-in-out;
    }
    .message-box button:hover {
      background-color: #DC2626; /* Red-600 */
    }
    /* Style for date input highlighting */
    .date-input-container {
      position: relative;
      display: flex;
      flex-direction: column;
    }
    .date-input-label {
      font-size: 0.75rem; /* text-xs */
      font-weight: 500; /* font-medium */
      color: #4B5563; /* gray-600 */
      margin-bottom: 0.25rem; /* mb-1 */
    }
    .date-highlight {
      background-color: #DBEAFE; /* blue-100 */
      border-color: #93C5FD; /* blue-300 */
    }
    .modal-close-btn {
      position: absolute;
      top: 10px;
      right: 15px;
      font-size: 1.5rem;
      font-weight: bold;
      cursor: pointer;
      color: #6B7280; /* gray-500 */
      background: none;
      border: none;
      padding: 0;
      line-height: 1;
    }
    .modal-close-btn:hover {
      color: #374151; /* gray-700 */
    }

    /* Custom styles for table container and sticky header */
    .table-container {
        max-height: 500px; /* Set a max height for vertical scrolling */
        overflow-y: auto; /* Enable vertical scrolling */
        overflow-x: scroll; /* Keep horizontal scrolling */
        border-radius: 8px; /* Apply rounded corners to the container */
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06); /* Add shadow */
        scrollbar-gutter: stable both-edges; /* Reserve space for the scrollbar */
    }

    .table-container thead th {
        position: sticky;
        top: 0;
        background-color: #2563EB; /* Tailwind blue-600 */
        color: white;
        z-index: 10; /* Ensure header is above scrolling content */
        /* Make sure the header matches the width of the content below */
        box-shadow: 0 2px 2px -1px rgba(0, 0, 0, 0.4); /* Add shadow to sticky header */
    }

    /* Webkit (Chrome, Safari) scrollbar styling for both scrollable divs */
    .table-container::-webkit-scrollbar {
      -webkit-appearance: none;
      width: 10px; /* Width of the vertical scrollbar */
      height: 10px; /* Height of the horizontal scrollbar */
    }

    .table-container::-webkit-scrollbar-track {
      background: #f1f1f1; /* Light grey track */
      border-radius: 5px;
    }

    .table-container::-webkit-scrollbar-thumb {
      background: #888; /* Darker grey thumb */
      border-radius: 5px;
    }

    .table-container::-webkit-scrollbar-thumb:hover {
      background: #555; /* Even darker grey on hover */
    }
  </style>
</head>
<body class="bg-gray-100 p-4 sm:p-8">
  <h1 class="text-3xl font-bold text-center text-gray-800 mb-8">Quantum Business Activity Dashboard</h1>

  <div id="messageBoxContainer"></div>

  <!-- Status Report Section -->
  <!-- Added sticky and top-0 to make the overview section stick to the top on scroll -->
  <div class="bg-white p-6 rounded-lg shadow-md mb-8 sticky top-0 z-10">
    <h2 class="text-2xl font-bold text-gray-800 mb-4">Business Activity Overview</h2>
    <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4 text-center">
      <div class="p-4 bg-blue-100 rounded-lg shadow">
        <p class="text-lg font-medium text-gray-700">Reports Pending</p>
        <p id="reportsPendingCount" class="text-3xl font-bold text-blue-800 mt-2">0</p>
      </div>
      <div class="p-4 bg-green-100 rounded-lg shadow">
        <p class="text-lg font-medium text-gray-700">Reports Sent</p>
        <p id="reportsSentCount" class="text-3xl font-bold text-green-800 mt-2">0</p>
      </div>
      <div class="p-4 bg-yellow-100 rounded-lg shadow">
        <p class="text-lg font-medium text-gray-700">Invoices Pending</p>
        <p id="invoicesPendingCount" class="text-3xl font-bold text-yellow-800 mt-2">0</p>
      </div>
      <div class="p-4 bg-purple-100 rounded-lg shadow">
        <p class="text-lg font-medium text-gray-700">Invoices Sent</p>
        <p id="invoicesSentCount" class="text-3xl font-bold text-purple-800 mt-2">0</p>
      </div>
      <div class="p-4 bg-red-100 rounded-lg shadow">
        <p class="text-lg font-medium text-gray-700">Payments Pending</p>
        <p id="paymentsPendingCount" class="text-3xl font-bold text-red-800 mt-2">0</p>
      </div>
      <div class="p-4 bg-teal-100 rounded-lg shadow">
        <p class="text-lg font-medium text-gray-700">Payments Received</p>
        <p id="paymentsReceivedCount" class="text-3xl font-bold text-teal-800 mt-2">0</p>
      </div>
    </div>
  </div>

  <!-- Buttons to open modals -->
  <!-- Added sticky and a calculated top position to make the buttons stick below the overview section -->
  <div class="flex justify-center gap-4 mb-8 sticky top-[180px] z-20 bg-gray-100 py-4">
    <button type="button" onclick="openFormModal()" class="bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 px-6 rounded-lg shadow-md transition duration-200 ease-in-out">Add / Edit Entry</button>
    <button type="button" onclick="openFilterModal()" class="bg-purple-600 hover:bg-purple-700 text-white font-semibold py-2 px-6 rounded-lg shadow-md transition duration-200 ease-in-out">Filters & Search</button>
  </div>

  <!-- Form Modal -->
  <div id="formModal" class="modal-overlay">
    <div class="modal-content">
      <button class="modal-close-btn" onclick="closeFormModal()">&times;</button>
      <h2 class="text-2xl font-bold text-gray-800 mb-4 text-center">Entry Form</h2>
      <form id="entryForm" class="bg-white p-6 rounded-lg shadow-md mb-8 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <input type="text" name="serial" id="serialNoInput" placeholder="Serial No." class="p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500">
        
        <div class="date-input-container">
          <label for="clientNameInput" class="date-input-label">Client Name</label>
          <input type="text" name="client" id="clientNameInput" placeholder="Client Name" list="clientNames" class="p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500">
          <datalist id="clientNames"></datalist>
        </div>

        <input type="text" name="inquiry" placeholder="Mode of Inquiry" class="p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500">
        <input type="text" name="poNumber" placeholder="PO Number" class="p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500">

        <div class="date-input-container">
          <label for="poDate" class="date-input-label">PO Date</label>
          <input type="date" id="poDate" name="poDate" class="p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 date-highlight">
        </div>

        <input type="text" name="site" placeholder="Site" class="p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500">
        <input type="text" name="jobDesc" placeholder="Job Description" class="p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500">
        <input type="text" name="team" placeholder="Team Members" class="p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500">
        
        <div class="date-input-container">
          <label for="visitDate" class="date-input-label">Date(s) of Visit</label>
          <!-- Changed type to text to allow comma-separated multiple dates -->
          <input type="text" id="visitDate" name="visitDate" placeholder="DD-MM-YYYY, DD-MM-YYYY, ..." class="p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 date-highlight">
        </div>

        <input type="text" name="shift" placeholder="Working Days / Shift" class="p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500">
        <input type="text" name="reportNo" placeholder="Report No." class="p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500">
        <select name="reportEmail" class="p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500">
          <option value="">Report Email Status</option>
          <option value="Sent">Sent</option>
          <option value="Pending">Pending</option>
          <option value="Not Required">Not Required</option>
        </select>
        <select name="reportCourier" class="p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500">
          <option value="">Report Courier Status</option>
          <option value="Sent">Sent</option>
          <option value="Pending">Pending</option>
          <option value="Not Required">Not Required</option>
        </select>
        <input type="text" name="invoiceNo" placeholder="Invoice No." class="p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500">
        <input type="text" name="invoiceAmt" placeholder="Invoice Amount" class="p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500">
        <select name="invoiceEmail" class="p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500">
          <option value="">Invoice Email Status</option>
          <option value="Sent">Sent</option>
          <option value="Pending">Pending</option>
          <option value="Not Required">Not Required</option>
        </select>
        <select name="invoiceCourier" class="p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500">
          <option value="">Invoice Courier Status</option>
          <option value="Sent">Sent</option>
          <option value="Pending">Pending</option>
          <option value="Not Required">Not Required</option>
        </select>
        <select name="paymentStatus" class="p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-500">
          <option value="">Payment Status</option>
          <option value="Received">Received</option>
          <option value="Pending">Pending</option>
          <option value="Partially Received">Partially Received</option>
        </select>

        <div class="date-input-container">
          <label for="paymentDate" class="date-input-label">Payment Received Date</label>
          <input type="date" id="paymentDate" name="paymentDate" class="p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 date-highlight">
        </div>

        <div class="col-span-full flex flex-wrap justify-center gap-4 mt-4">
          <button type="submit" class="bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 px-6 rounded-lg shadow-md transition duration-200 ease-in-out">Add / Update Entry</button>
          <button type="button" onclick="cancelEditAndCloseForm()" class="bg-gray-500 hover:bg-gray-600 text-white font-semibold py-2 px-6 rounded-lg shadow-md transition duration-200 ease-in-out">Cancel</button>
          <button type="button" onclick="exportToExcel()" class="bg-green-600 hover:bg-green-700 text-white font-semibold py-2 px-6 rounded-lg shadow-md transition duration-200 ease-in-out">Export Excel</button>
          <button type="button" onclick="exportToPDF()" class="bg-red-600 hover:bg-red-700 text-white font-semibold py-2 px-6 rounded-lg shadow-md transition duration-200 ease-in-out">Export PDF</button>
        </div>
      </form>
    </div>
  </div>

  <!-- Filter Modal -->
  <div id="filterModal" class="modal-overlay">
    <div class="modal-content">
      <button class="modal-close-btn" onclick="closeFilterModal()">&times;</button>
      <h2 class="text-2xl font-bold text-gray-800 mb-4 text-center">Filters & Search</h2>
      <div class="bg-white p-6 rounded-lg shadow-md grid grid-cols-1 md:grid-cols-2 gap-4">
        <div class="flex flex-col">
          <label for="clientSearch" class="text-sm font-medium text-gray-700 mb-1">Search Client Name</label>
          <input type="text" id="clientSearch" placeholder="Search by Client Name" class="p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500">
        </div>

        <div class="flex flex-col">
          <label for="filterReportEmail" class="text-sm font-medium text-gray-700 mb-1">Report Email Status</label>
          <select id="filterReportEmail" class="p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500">
            <option value="All">All</option>
            <option value="Sent">Sent</option>
            <option value="Pending">Pending</option>
            <option value="Not Required">Not Required</option>
          </select>
        </div>
        <div class="flex flex-col">
          <label for="filterReportCourier" class="text-sm font-medium text-gray-700 mb-1">Report Courier Status</label>
          <select id="filterReportCourier" class="p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500">
            <option value="All">All</option>
            <option value="Sent">Sent</option>
            <option value="Pending">Pending</option>
            <option value="Not Required">Not Required</option>
          </select>
        </div>
        <div class="flex flex-col">
          <label for="filterInvoiceEmail" class="text-sm font-medium text-gray-700 mb-1">Invoice Email Status</label>
          <select id="filterInvoiceEmail" class="p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500">
            <option value="All">All</option>
            <option value="Sent">Sent</option>
            <option value="Pending">Pending</option>
            <option value="Not Required">Not Required</option>
          </select>
        </div>
        <div class="flex flex-col">
          <label for="filterInvoiceCourier" class="text-sm font-medium text-gray-700 mb-1">Invoice Courier Status</label>
          <select id="filterInvoiceCourier" class="p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500">
            <option value="All">All</option>
            <option value="Sent">Sent</option>
            <option value="Pending">Pending</option>
            <option value="Not Required">Not Required</option>
          </select>
        </div>
        <div class="flex flex-col">
          <label for="filterPaymentStatus" class="text-sm font-medium text-gray-700 mb-1">Payment Status</label>
          <select id="filterPaymentStatus" class="p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500">
            <option value="All">All</option>
            <option value="Received">Received</option>
            <option value="Pending">Pending</option>
            <option value="Partially Received">Partially Received</option>
          </select>
        </div>
        <div class="col-span-full flex flex-wrap justify-center gap-4 mt-4">
          <button type="button" onclick="applyFiltersAndCloseModal()" class="bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 px-6 rounded-lg shadow-md transition duration-200 ease-in-out">Apply Filters</button>
          <button type="button" onclick="closeFilterModal()" class="bg-gray-500 hover:bg-gray-600 text-white font-semibold py-2 px-6 rounded-lg shadow-md transition duration-200 ease-in-out">Close</button>
        </div>
      </div>
    </div>
  </div>


  <!-- Table container with vertical and horizontal scrolling -->
  <div class="table-container">
    <table id="dashboardTable" class="min-w-[2000px] bg-white">
      <thead>
        <tr>
          <th class="py-3 px-4 bg-blue-600 text-white text-left text-sm font-semibold uppercase tracking-wider rounded-tl-lg">Serial No.</th>
          <th class="py-3 px-4 bg-blue-600 text-white text-left text-sm font-semibold uppercase tracking-wider">Client Name</th>
          <th class="py-3 px-4 bg-blue-600 text-white text-left text-sm font-semibold uppercase tracking-wider">Mode of Inquiry</th>
          <th class="py-3 px-4 bg-blue-600 text-white text-left text-sm font-semibold uppercase tracking-wider">PO Number</th>
          <th class="py-3 px-4 bg-blue-600 text-white text-left text-sm font-semibold uppercase tracking-wider">PO Date</th>
          <th class="py-3 px-4 bg-blue-600 text-white text-left text-sm font-semibold uppercase tracking-wider">Site</th>
          <th class="py-3 px-4 bg-blue-600 text-white text-left text-sm font-semibold uppercase tracking-wider">Job Description</th>
          <th class="py-3 px-4 bg-blue-600 text-white text-left text-sm font-semibold uppercase tracking-wider">Team Members</th>
          <th class="py-3 px-4 bg-blue-600 text-white text-left text-sm font-semibold uppercase tracking-wider">Date of Visit</th>
          <th class="py-3 px-4 bg-blue-600 text-white text-left text-sm font-semibold uppercase tracking-wider">Working Days / Shift</th>
          <th class="py-3 px-4 bg-blue-600 text-white text-left text-sm font-semibold uppercase tracking-wider">Report No.</th>
          <th class="py-3 px-4 bg-blue-600 text-white text-left text-sm font-semibold uppercase tracking-wider">Report Email Status</th>
          <th class="py-3 px-4 bg-blue-600 text-white text-left text-sm font-semibold uppercase tracking-wider">Report Courier Status</th>
          <th class="py-3 px-4 bg-blue-600 text-white text-left text-sm font-semibold uppercase tracking-wider">Invoice No.</th>
          <th class="py-3 px-4 bg-blue-600 text-white text-left text-sm font-semibold uppercase tracking-wider">Invoice Amount</th>
          <th class="py-3 px-4 bg-blue-600 text-white text-left text-sm font-semibold uppercase tracking-wider">Invoice Email Status</th>
          <th class="py-3 px-4 bg-blue-600 text-white text-left text-sm font-semibold uppercase tracking-wider">Invoice Courier Status</th>
          <th class="py-3 px-4 bg-blue-600 text-white text-left text-sm font-semibold uppercase tracking-wider">Payment Status</th>
          <th class="py-3 px-4 bg-blue-600 text-white text-left text-sm font-semibold uppercase tracking-wider rounded-tr-lg">Payment Received Date</th>
          <th class="py-3 px-4 bg-blue-600 text-white text-left text-sm font-semibold uppercase tracking-wider">Actions</th>
        </tr>
      </thead>
      <tbody>
        <!-- Table rows will be added here by JavaScript -->
      </tbody>
    </table>
  </div>

  <script>
    // Get modal elements
    const formModal = document.getElementById('formModal');
    const filterModal = document.getElementById('filterModal');

    // Selectors for form and table elements
    const form = document.getElementById('entryForm'); // Form is now inside a modal
    const tableBody = document.querySelector('#dashboardTable tbody');
    let editRowIndex = null;
    const messageBoxContainer = document.getElementById('messageBoxContainer');
    const serialNoInput = document.getElementById('serialNoInput');
    const clientNameInput = document.getElementById('clientNameInput');
    const clientNamesDatalist = document.getElementById('clientNames');
    const clientSearchInput = document.getElementById('clientSearch');
    const filterReportEmail = document.getElementById('filterReportEmail');
    const filterReportCourier = document.getElementById('filterReportCourier');
    const filterInvoiceEmail = document.getElementById('filterInvoiceEmail');
    const filterInvoiceCourier = document.getElementById('filterInvoiceCourier'); 
    const filterPaymentStatus = document.getElementById('filterPaymentStatus');

    // Status counters
    const reportsPendingCount = document.getElementById('reportsPendingCount');
    const reportsSentCount = document.getElementById('reportsSentCount');
    const invoicesPendingCount = document.getElementById('invoicesPendingCount');
    const invoicesSentCount = document.getElementById('invoicesSentCount');
    const paymentsPendingCount = document.getElementById('paymentsPendingCount');
    const paymentsReceivedCount = document.getElementById('paymentsReceivedCount');

    let uniqueClientNames = new Set();

    // Modal control functions
    function openFormModal() {
      formModal.classList.add('active');
      // When opening the form, if not in edit mode, ensure serial is editable
      if (editRowIndex === null) {
        serialNoInput.readOnly = false;
        updateNextSerialNumber(); 
      }
    }

    function closeFormModal() {
      formModal.classList.remove('active');
    }

    function openFilterModal() {
      filterModal.classList.add('active');
    }

    function closeFilterModal() {
      filterModal.classList.remove('active');
    }

    // Function to display a custom message box (used for delete confirmation)
    function showMessageBox(title, message, onConfirm) {
      console.log("showMessageBox called:", title); // Debug log

      // Create main modal overlay element
      const messageOverlay = document.createElement('div');
      messageOverlay.classList.add('modal-overlay', 'active');

      // Create modal content element
      const modalContent = document.createElement('div');
      modalContent.classList.add('message-box', 'modal-content');

      // Add inner HTML for title, message, and buttons
      modalContent.innerHTML = `
        <h3>${title}</h3>
        <p>${message}</p>
        <button id="messageBoxConfirmBtn" class="bg-red-600 hover:bg-red-700 text-white font-semibold py-2 px-6 rounded-lg shadow-md transition duration-200 ease-in-out">Confirm</button>
        <button id="messageBoxCancelBtn" class="ml-2 bg-gray-500 hover:bg-gray-600 text-white font-semibold py-2 px-6 rounded-lg shadow-md transition duration-200 ease-in-out">Cancel</button>
      `;

      // Append content to overlay
      messageOverlay.appendChild(modalContent);

      // Append overlay to container
      messageBoxContainer.appendChild(messageOverlay);

      // Get buttons from the newly created modal
      const confirmBtn = modalContent.querySelector('#messageBoxConfirmBtn');
      const cancelBtn = modalContent.querySelector('#messageBoxCancelBtn');

      console.log("Buttons retrieved:", { confirmBtn, cancelBtn }); // Debug log

      // Attach event listeners
      confirmBtn.onclick = () => {
        console.log("Confirm button clicked"); // Debug log
        onConfirm(true);
        messageOverlay.remove(); // Remove the overlay element
        console.log("Message overlay removed (confirmed)"); // Debug log
      };
      cancelBtn.onclick = () => {
        console.log("Cancel button clicked"); // Debug log
        onConfirm(false);
        messageOverlay.remove(); // Remove the overlay element
        console.log("Message overlay removed (cancelled)"); // Debug log
      };
    }

    // Function to format date(s) from ISO (YYYY-MM-DD) or Indian (DD-MM-YYYY) to DD-MM-YYYY for display
    function formatDateToIndian(dateString) {
      if (!dateString) return '';
      const dates = dateString.split(',').map(s => s.trim());
      return dates.map(dateStr => {
        let date = new Date(dateStr);
        if (isNaN(date.getTime())) {
            // Try parsing as DD-MM-YYYY if ISO failed
            const parts = dateStr.split('-');
            if (parts.length === 3) {
                date = new Date(`${parts[2]}-${parts[1]}-${parts[0]}`);
            }
        }
        if (isNaN(date.getTime())) {
            return dateStr; // Return original string if still invalid
        }
        const day = String(date.getDate()).padStart(2, '0');
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const year = date.getFullYear();
        return `${day}-${month}-${year}`;
      }).join(', ');
    }

    // Function to format date(s) from DD-MM-YYYY to ISO (YYYY-MM-DD) for storage/input fields
    function formatDateToISO(dateString) {
        if (!dateString) return '';
        const dates = dateString.split(',').map(s => s.trim());
        return dates.map(dateStr => {
            const parts = dateStr.split('-');
            if (parts.length === 3 && !isNaN(parts[0]) && !isNaN(parts[1]) && !isNaN(parts[2])) {
                return `${parts[2]}-${parts[1]}-${parts[0]}`;
            }
            return dateStr; // Return original string if not in DD-MM-YYYY format
        }).join(',');
    }

    // Function to clear the form and reset edit state, and close the form modal
    function cancelEditAndCloseForm() {
      form.reset();
      if (editRowIndex !== null) {
        tableBody.children[editRowIndex].classList.remove('bg-yellow-100');
        editRowIndex = null;
      }
      document.querySelector('#entryForm button[type="submit"]').textContent = 'Add / Update Entry';
      serialNoInput.readOnly = false; // Make serial number editable when cancelling edit/adding new
      updateNextSerialNumber();
      closeFormModal();
    }

    // Define the order of fields as they appear in the form/table header
    const formFieldNames = [
      'serial', 'client', 'inquiry', 'poNumber', 'poDate', 'site', 'jobDesc', 'team',
      'visitDate', 'shift', 'reportNo', 'reportEmail', 'reportCourier', 'invoiceNo',
      'invoiceAmt', 'invoiceEmail', 'invoiceCourier', 'paymentStatus', 'paymentDate'
    ];

    // Function to add or update a row in the table
    function addRow(data, isEdit = false) {
      const row = document.createElement('tr');
      row.classList.add('hover:bg-gray-50', 'transition', 'duration-150', 'ease-in-out', 'border-b', 'border-gray-200');

      const getFormElementValue = (name) => {
        const element = form.elements[name];
        if (!element) return '';
        return element.value;
      };

      let rowValues;
      if (Array.isArray(data)) {
        rowValues = data;
      } else {
        rowValues = formFieldNames.map(name => getFormElementValue(name));
      }

      rowValues.forEach((value, index) => {
        const td = document.createElement('td');
        td.classList.add('py-2', 'px-4', 'text-sm', 'text-gray-700', 'truncate');
        
        // Only allow inline editing for columns other than Serial No. (index 0)
        if (index !== 0) { 
          td.contentEditable = true; 
        }

        if ([4, 8, 18].includes(index)) { // poDate, visitDate, paymentDate
          td.textContent = formatDateToIndian(value);
        } else {
          td.textContent = value;
        }
        row.appendChild(td);
      });

      if (rowValues[1]) {
        uniqueClientNames.add(rowValues[1]);
      }

      const actionsTd = document.createElement('td');
      actionsTd.classList.add('py-2', 'px-4', 'text-sm', 'text-gray-700', 'whitespace-nowrap');

      const editBtn = document.createElement('button');
      editBtn.textContent = 'Edit';
      editBtn.classList.add('text-blue-600', 'hover:text-blue-800', 'font-medium', 'mr-2');
      editBtn.onclick = () => {
        // Remove highlight from other rows and highlight current row
        tableBody.querySelectorAll('tr').forEach(r => r.classList.remove('bg-yellow-100'));
        row.classList.add('bg-yellow-100');

        const cells = Array.from(row.querySelectorAll('td'));
        formFieldNames.forEach((name, i) => {
            const input = form.elements[name];
            if (input && cells[i]) {
                const cellValue = cells[i].textContent.trim();
                // Special handling for date inputs and multiselect (visitDate)
                if ([4, 18].includes(i) && input.type === 'date') {
                    const isoDates = formatDateToISO(cellValue).split(',');
                    input.value = isoDates[0] || ''; // Only take the first date for single date inputs
                } else if (i === 8 && input.type === 'text') { // visitDate, which is text input
                    input.value = formatDateToISO(cellValue);
                } else if (input.tagName === 'SELECT') {
                    input.value = cellValue;
                } else {
                    input.value = cellValue;
                }
            }
        });

        // Set serial number to readOnly when editing
        serialNoInput.readOnly = true;

        editRowIndex = Array.from(tableBody.children).indexOf(row);
        document.querySelector('#entryForm button[type="submit"]').textContent = 'Update Entry';
        openFormModal(); // Open the form modal for editing
      };

      const deleteBtn = document.createElement('button');
      deleteBtn.textContent = 'Delete';
      deleteBtn.classList.add('text-red-600', 'hover:text-red-800', 'font-medium');
      deleteBtn.onclick = () => {
        console.log("Delete button clicked for row:", row); // Debug log
        showMessageBox(
          'Confirm Deletion',
          'Are you sure you want to delete this entry?',
          (confirmed) => {
            console.log("Confirmation callback received:", confirmed); // Debug log
            if (confirmed) {
              row.remove(); // Remove the row
              reindexTableSerials(); // Re-index serial numbers, save data, update counts
              cancelEditAndCloseForm(); // Close form modal after deletion if open
              console.log("Entry deleted and data reloaded."); // Debug log
            } else {
              console.log("Deletion cancelled."); // Debug log
            }
          }
        );
      };

      actionsTd.appendChild(editBtn);
      actionsTd.appendChild(deleteBtn);
      row.appendChild(actionsTd);

      if (isEdit && editRowIndex !== null) {
        tableBody.replaceChild(row, tableBody.children[editRowIndex]);
        editRowIndex = null;
      } else {
        tableBody.appendChild(row);
      }
    }

    /**
     * Re-indexes the serial numbers in the table to be continuous (1, 2, 3...)
     * and then saves the updated data, refreshes datalists, and updates status counts.
     */
    function reindexTableSerials() {
        const rows = Array.from(tableBody.rows);
        rows.forEach((row, index) => {
            // Update the text content of the first cell (serial number)
            if (row.cells[0]) {
                row.cells[0].textContent = index + 1;
            }
        });
        saveData();
        updateClientDatalist();
        updateNextSerialNumber();
        filterTable(); // Re-apply filters as rows might have shifted visually
        updateStatusCounts();
        console.log("Table serial numbers re-indexed."); // Debug log
    }

    // Event listener for form submission
    form.addEventListener('submit', function(e) {
      e.preventDefault();
      addRow(null, editRowIndex !== null); // Add or update row based on editRowIndex
      form.reset(); // Clear the form
      tableBody.querySelectorAll('tr').forEach(r => r.classList.remove('bg-yellow-100')); // Remove any row highlighting
      serialNoInput.readOnly = false; // Make serial number editable for new entries
      reindexTableSerials(); // Re-index after any add/update operation
      closeFormModal(); // Close modal after submission
    });

    // Function to save data to localStorage
    function saveData() {
      const rows = Array.from(tableBody.rows).map(row =>
        Array.from(row.cells).slice(0, -1).map((cell, cellIndex) => { // Exclude the 'Actions' column
            // For serial number (index 0), get the re-indexed value
            const valueToSave = (cellIndex === 0) ? parseInt(cell.textContent.trim()) : cell.textContent.trim();
            
            const headerCell = document.getElementById('dashboardTable').querySelector('thead tr').cells[cellIndex];
            const headerText = headerCell ? headerCell.textContent.trim() : '';

            // Format dates back to ISO for storage
            if (['PO Date', 'Date of Visit', 'Payment Received Date'].includes(headerText)) {
                return formatDateToISO(cell.textContent.trim());
            }
            return valueToSave;
        })
      );
      localStorage.setItem('dashboardData', JSON.stringify(rows));
      console.log("Data saved to localStorage."); // Debug log
    }

    // Function to load data from localStorage
    function loadData() {
      const data = JSON.parse(localStorage.getItem('dashboardData') || '[]');
      uniqueClientNames.clear(); // Clear existing unique client names
      const tempRows = [];
      data.forEach(rowData => {
          tempRows.push(rowData);
          if (rowData[1]) { // Assuming client name is at index 1
            uniqueClientNames.add(rowData[1]);
          }
      });
      tableBody.innerHTML = ''; // Clear current table body
      tempRows.forEach(row => addRow(row)); // Add loaded data to the table
      reindexTableSerials(); // Re-index after loading
      console.log("Data loaded from localStorage."); // Debug log
    }

    // Function to update the client names datalist for the form
    function updateClientDatalist() {
        clientNamesDatalist.innerHTML = '';
        Array.from(uniqueClientNames).sort().forEach(client => {
            const option = document.createElement('option');
            option.value = client;
            clientNamesDatalist.appendChild(option);
        });
    }

    // Function to get the next available serial number
    function updateNextSerialNumber() {
        let maxSerial = 0;
        Array.from(tableBody.rows).forEach(row => {
            if (row.cells[0] && row.cells[0].textContent) {
                const serial = parseInt(row.cells[0].textContent.trim());
                if (!isNaN(serial) && serial > maxSerial) {
                    maxSerial = serial;
                }
            }
        });
        serialNoInput.value = maxSerial + 1;
    }

    // Function to filter table rows based on criteria (called when filters applied)
    function filterTable() {
        const clientSearchTerm = clientSearchInput.value.toLowerCase();
        const reportEmailFilter = filterReportEmail.value;
        const reportCourierFilter = filterReportCourier.value;
        const invoiceEmailFilter = filterInvoiceEmail.value;
        const invoiceCourierFilter = filterInvoiceCourier.value;
        const paymentStatusFilter = filterPaymentStatus.value;

        Array.from(tableBody.rows).forEach(row => {
            const cells = row.cells;
            const clientName = cells[1].textContent.toLowerCase();
            const reportEmailStatus = cells[11].textContent.trim();
            const reportCourierStatus = cells[12].textContent.trim();
            const invoiceEmailStatus = cells[15].textContent.trim();
            const invoiceCourierStatus = cells[16].textContent.trim();
            const paymentStatus = cells[17].textContent.trim();

            const matchesClient = clientName.includes(clientSearchTerm);
            const matchesReportEmail = (reportEmailFilter === 'All' || reportEmailStatus === reportEmailFilter);
            const matchesReportCourier = (reportCourierFilter === 'All' || reportCourierStatus === reportCourierFilter);
            const matchesInvoiceEmail = (invoiceEmailFilter === 'All' || invoiceEmailStatus === invoiceEmailFilter);
            const matchesInvoiceCourier = (invoiceCourierFilter === 'All' || invoiceCourierStatus === invoiceCourierFilter);
            const matchesPaymentStatus = (paymentStatusFilter === 'All' || paymentStatus === paymentStatusFilter);

            if (matchesClient && matchesReportEmail && matchesReportCourier && matchesInvoiceEmail && matchesInvoiceCourier && matchesPaymentStatus) {
                row.style.display = ''; // Show row
            } else {
                row.style.display = 'none'; // Hide row
            }
        });
    }

    // Function to apply filters and close the modal
    function applyFiltersAndCloseModal() {
        filterTable();
        closeFilterModal();
    }

    // Function to update the status counts displayed in the overview section
    function updateStatusCounts() {
        let reportsPending = 0;
        let reportsSent = 0;
        let invoicesPending = 0;
        let invoicesSent = 0;
        let paymentsPending = 0;
        let paymentsReceived = 0;

        Array.from(tableBody.rows).forEach(row => {
            const cells = row.cells;
            const reportEmailStatus = cells[11].textContent.trim();
            const reportCourierStatus = cells[12].textContent.trim();
            const invoiceEmailStatus = cells[15].textContent.trim();
            const invoiceCourierStatus = cells[16].textContent.trim();
            const paymentStatus = cells[17].textContent.trim();

            if ((reportEmailStatus === 'Pending' || reportEmailStatus === '') || (reportCourierStatus === 'Pending' || reportCourierStatus === '')) {
                reportsPending++;
            } else if (reportEmailStatus === 'Sent' || reportCourierStatus === 'Sent') {
                reportsSent++;
            }

            if ((invoiceEmailStatus === 'Pending' || invoiceEmailStatus === '') || (invoiceCourierStatus === 'Pending' || invoiceCourierStatus === '')) {
                invoicesPending++;
            } else if (invoiceEmailStatus === 'Sent' || invoiceCourierStatus === 'Sent') {
                invoicesSent++;
            }

            if (paymentStatus === 'Pending' || paymentStatus === 'Partially Received' || paymentStatus === '') {
                paymentsPending++;
            } else if (paymentStatus === 'Received') {
                paymentsReceived++;
            }
        });

        reportsPendingCount.textContent = reportsPending;
        reportsSentCount.textContent = reportsSent;
        invoicesPendingCount.textContent = invoicesPending;
        invoicesSentCount.textContent = invoicesSent;
        paymentsPendingCount.textContent = paymentsPending;
        paymentsReceivedCount.textContent = paymentsReceived;
    }

    // Attach event listeners for filtering fields within the modal
    clientSearchInput.addEventListener('input', filterTable);
    filterReportEmail.addEventListener('change', filterTable);
    filterReportCourier.addEventListener('change', filterTable);
    filterInvoiceEmail.addEventListener('change', filterTable);
    filterInvoiceCourier.addEventListener('change', filterInvoiceCourier);
    filterPaymentStatus.addEventListener('change', filterTable);


    // Function to export table data to Excel
    function exportToExcel() {
      const table = document.getElementById('dashboardTable');
      const wb = XLSX.utils.table_to_book(table, { sheet: 'Dashboard' });
      XLSX.writeFile(wb, 'dashboard.xlsx');
    }

    // Function to export table data to PDF
    async function exportToPDF() {
      const { jsPDF } = window.jspdf;
      const doc = new jsPDF('l', 'pt', 'a4');
      const table = document.getElementById('dashboardTable');

      const headers = Array.from(table.querySelectorAll('thead th')).map(th => th.textContent.trim());
      const filteredHeaders = headers.filter(header => header !== 'Actions'); // Exclude 'Actions' column from PDF

      const rows = Array.from(table.querySelectorAll('tbody tr')).map(row => {
          return Array.from(row.querySelectorAll('td')).slice(0, -1).map(cell => cell.textContent.trim()); // Exclude 'Actions' column data
      });

      doc.autoTable({
        head: [filteredHeaders],
        body: rows,
        startY: 20,
        styles: { fontSize: 8, cellPadding: 5, overflow: 'linebreak' },
        headStyles: { fillColor: [0, 123, 255], textColor: 255, fontStyle: 'bold' },
        alternateRowStyles: { fillColor: [240, 240, 240] },
        didDrawPage: function(data) {
          let str = "Page " + doc.internal.getNumberOfPages();
          doc.setFontSize(10);
          doc.text(str, doc.internal.pageSize.width - data.settings.margin.right, doc.internal.pageSize.height - 10);
        }
      });

      doc.save('dashboard.pdf');
    }

    // Load data when the page loads
    window.addEventListener('load', () => {
        loadData();
        filterTable();
    });
    // Save data when there's an input change in the table (for inline editing)
    tableBody.addEventListener('input', () => {
        // If the edited cell is not the serial number, then save data
        // The serial number is now programmatically controlled.
        saveData();
        updateClientDatalist();
        filterTable();
        updateStatusCounts();
    });
  </script>
</body>
</html>
"""

# Create a temporary HTML file to load into webview
# This is a common pattern when dealing with larger HTML content or local assets.
temp_html_path = "index.html"
with open(temp_html_path, "w", encoding="utf-8") as f:
    f.write(html_content)

# Create the webview window
# url='index.html' tells webview to load the local index.html file.
# You can also pass the html_content directly using html=html_content parameter,
# but using a file can sometimes simplify relative paths for assets if you add any.
webview.create_window(
    "Quantum Business Activity Dashboard",
    url=temp_html_path,
    width=1200,  # Set an initial width for the window
    height=800,  # Set an initial height for the window
    min_size=(800, 600) # Set a minimum size for responsiveness
)

# Start the webview application loop
webview.start()

# Clean up the temporary HTML file after the application closes
os.remove(temp_html_path)
