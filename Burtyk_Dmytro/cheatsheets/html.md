Text & Formatting

<h1>Main Title (Only 1 per page)</h1>
<h2>Section Title</h2>
<h6>Smallest Heading</h6>

<p>Standard paragraph of text.</p>
<span>Inline container (doesn't break to a new line)</span>

<strong>Important / Bold</strong>
<em>Emphasized / Italic</em>
<mark>Highlighted text</mark>
<small>Smaller text (like copyright)</small>
<del>Crossed out text</del>
<u>Underlined text</u>
<blockquote>Block quotation</blockquote>

<br> <hr> ```

---

 Links (Anchors)
```html
<a href="[https://google.com](https://google.com)">Go to Google</a>

<a href="page.html" target="_blank">New Tab</a>

<a href="mailto:support@mystore.com">Email Us</a>
<a href="tel:+420800123456">Call Us</a>

<a href="#footer-section">Jump to Footer</a>
<div id="footer-section">You jumped here!</div>

Images & Multimedia

<img src="logo.png" alt="Description for blind users" width="200" height="100">

<a href="home.html"><img src="logo.png" alt="Home"></a>

<video width="320" height="240" controls>
    <source src="movie.mp4" type="video/mp4">
</video>

<audio controls>
    <source src="music.mp3" type="audio/mpeg">
</audio>

<iframe src="[https://www.youtube.com/embed/](https://www.youtube.com/embed/)..." width="500" height="300"></iframe>

Lists (Bullet points & Numbers)

<ul>
    <li>First item</li>
    <li>Second item</li>
</ul>

<ol>
    <li>Step One</li>
    <li>Step Two</li>
</ol>

<dl>
    <dt>Term (e.g., RAM)</dt>
    <dd>Definition (e.g., Random Access Memory)</dd>
</dl>

Tables (Exam Favorite!)

<table border="1">
    <thead> <tr> <th>Product</th> <th>Price</th>
        </tr>
    </thead>
    <tbody> <tr>
            <td>Laptop</td> <td>$999</td>
        </tr>
        <tr>
            <td colspan="2">Spans across 2 columns!</td>
        </tr>
    </tbody>
</table>

Forms & Inputs

<form action="/submit" method="POST">
    
    <label for="user">Username:</label>
    <input type="text" id="user" name="username" placeholder="Enter name" required>
    
    <label for="pass">Password:</label>
    <input type="password" id="pass" name="password">

    <input type="email" name="email">
    <input type="number" name="qty" min="1" max="10">
    <input type="tel" name="phone">
    <input type="date" name="birthday">
    
    <input type="radio" name="color" value="red" id="red"> <label for="red">Red</label>
    <input type="radio" name="color" value="blue" id="blue"> <label for="blue">Blue</label>

    <input type="checkbox" name="rules" id="rules"> <label for="rules">I agree</label>

    <select name="country">
        <option value="US">USA</option>
        <option value="CZ" selected>Czechia</option> </select>

    <textarea name="message" rows="4" cols="50">Enter message here...</textarea>

    <button type="submit">Submit Form</button>
    <button type="reset">Clear Form</button>
</form>

Semantic Layout Tags

<header>Top of page (Logo, Navbar)</header>
<nav>Main Navigation links</nav>

<main>The core content of the page</main>
<section>A thematic grouping (e.g., "About Us", "Contact")</section>
<article>Independent content (Blog post, Product card)</article>
<aside>Sidebar content</aside>

<footer>Bottom of page (Copyright, links)</footer>

<div>Block-level container</div>
<span>Inline-level container</span>

Global Attributes

<div id="unique-name">ID must be unique on the page</div>
<div class="group-name">Classes can be used on multiple elements</div>
<div style="color: red;">Inline CSS (Avoid if possible)</div>
<div title="Hover text!">Hover your mouse over me</div>
<div hidden>This element is completely invisible</div>
<div data-price="99">Custom data attribute (Great for JavaScript/Django)</div>