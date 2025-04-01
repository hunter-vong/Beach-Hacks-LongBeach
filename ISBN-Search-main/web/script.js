let backButtonCreated = false;

function submitISBN() {
    const isbn = document.getElementById('isbn').value.trim();
    if (isbn) {
        fetch(`https://www.googleapis.com/books/v1/volumes?q=isbn:${isbn}`)
            .then(response => response.json())
            .then(data => {
                if (data.items && data.items.length > 0) {
                    const book = data.items[0].volumeInfo;
                    displayBookInfo(book);
                    fetchSimilarBooks(book.categories ? book.categories[0] : null);
                    fetchRecommendedBooks(book.categories ? book.categories[0] : null);
                } else {
                    alert("No book found for this ISBN.");
                }
            })
            .catch(error => {
                console.error("Error fetching book information:", error);
                alert("Error fetching book information. Please try again later.");
            });
    } else {
        alert("Please enter a valid ISBN number.");
    }
}

function fetchSimilarBooks(category) {
    if (category) {
        fetch(`https://www.googleapis.com/books/v1/volumes?q=subject:${encodeURIComponent(category)}`)
            .then(response => response.json())
            .then(data => {
                if (data.items && data.items.length > 1) {
                    displaySimilarBooks(data.items.slice(1, 4));
                }
            })
            .catch(error => console.error("Error fetching similar books:", error));
    }
}

function fetchRecommendedBooks(category) {
    if (category) {
        fetch(`https://www.googleapis.com/books/v1/volumes?q=subject:${encodeURIComponent(category)}`)
            .then(response => response.json())
            .then(data => {
                if (data.items && data.items.length > 5) {
                    displayRecommendedBooks(data.items.slice(0, 5));
                }
            })
            .catch(error => console.error("Error fetching recommended books:", error));
    }
}

function displayBookInfo(book) {
    const title = book.title || "No title available";
    const author = book.authors ? book.authors.join(', ') : "No author information available";
    const description = book.description || "No description available";
    const imageUrl = book.imageLinks ? book.imageLinks.thumbnail : null;
    
    document.getElementById('book-title').textContent = title;
    document.getElementById('book-author').textContent = "Author(s): " + author;
    document.getElementById('book-description').textContent = description;
    
    const bookImageElement = document.getElementById('book-image');
    if (imageUrl) {
        bookImageElement.src = imageUrl;
        bookImageElement.style.display = 'block';
    } else {
        bookImageElement.style.display = 'none';
    }
    
    document.getElementById('book-info').style.display = 'block';
}

function displaySimilarBooks(books) {
    const similarBooksContainer = document.getElementById('similar-books');
    similarBooksContainer.innerHTML = "";  // Clear previous results

    books.forEach(bookData => {
        const book = bookData.volumeInfo;
        const imageUrl = book.imageLinks ? book.imageLinks.thumbnail : "";

        if (imageUrl) {
            const img = document.createElement('img');
            img.src = imageUrl;
            img.alt = "Similar Book";
            img.classList.add('clickable-book');

            // Make the book image clickable to fetch and display details
            img.onclick = () => displayBookInfo(book);

            similarBooksContainer.appendChild(img);
        }
    });

    similarBooksContainer.style.display = 'block';
}

function displayRecommendedBooks(books) {
    const recommendedBooksContainer = document.getElementById('recommended-books');
    recommendedBooksContainer.innerHTML = "";
    books.forEach(bookData => {
        const book = bookData.volumeInfo;
        const title = book.title || "No title available";
        
        const bookElement = document.createElement('p');
        bookElement.textContent = title;
        bookElement.classList.add('recommended-book');
        
        recommendedBooksContainer.appendChild(bookElement);
    });
    recommendedBooksContainer.style.display = 'block';
}

function changeBarContent() {
    document.getElementById('isbn-label-text').textContent = 'Search Book Using ISBN Number';
    document.querySelector('.right-side').style.display = 'none';
}

function resetBarContent() {
    document.getElementById('isbn-label-text').textContent = 'Enter ISBN Number';
    document.querySelector('.right-side').style.display = 'flex';
    backButtonCreated = false;
}

function displayBookInfo(book) {
    const title = book.title || "No title available";
    const author = book.authors ? book.authors.join(', ') : "No author information available";
    const description = book.description || "No description available";
    const imageUrl = book.imageLinks ? book.imageLinks.thumbnail : null;
    
    document.getElementById('book-title').textContent = title;
    document.getElementById('book-author').textContent = "Author(s): " + author;
    document.getElementById('book-description').textContent = description;
    
    const bookImageElement = document.getElementById('book-image');
    if (imageUrl) {
        bookImageElement.src = imageUrl;
        bookImageElement.style.display = 'block';

        // Small delay to ensure the transition applies correctly
        setTimeout(() => {
            bookImageElement.classList.add('show');
        }, 50);
    } else {
        bookImageElement.style.display = 'none';
    }
    
    document.getElementById('book-info').style.display = 'block';
}
