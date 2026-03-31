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

# HTML Cheat Sheet
A reminder of HTML elements.

## Table of Contents
 - [Minimal page](#minimal-page)
 - [Head](#head)
 - [Text content](#text-content)
   - [Headings](#headings)
   - [Paragraphs](#paragraphs)
   - [Formatting](#formatting)
   - [Quotes](#quotes)
 - [Content](#content)
   - [Links](#links)
   - [Images](#images)
   - [Blocks](#blocks)
 - [Lists](#lists)
   - [Unordered list](#unordered-list)
   - [Ordered list](#ordered-list)
   - [Definition list](#definition-list)
 - [Tables](#tables)
   - [Basic table](#basic-table)
   - [Advanced table](#advanced-table)
 - [Forms](#forms)
 - [HTML5 Semantic](#html5-semantic)
   - [Page layout](#page-layout)
   - [New elements](#new-elements)

## Minimal page
```html
<!DOCTYPE html>
<html>
    <head>
        <meta charset="UTF-8">
        <title>Title</title>
    </head>
    <body>
        <!-- content here -->
    </body>
</html>
```

## Head
```html
<head>
    <title>Title</title>
    <base href="base-url" />
    <link href="style.css" rel="stylesheet" type="text/css" />
    <style type="text/css">
        /* CSS code */
    </style>
    <script src="script.js"></script>
    <script>
        // Javascript code
    </script>
    <meta charset="UTF-8">
    <meta name="keywords" content="keywords">
    <meta name="description" content="description">
    <meta name="author" content="name">
    <meta http-equiv="refresh" content="10">
</head>
```

tag | element
--- | ---
**title** | page title
**base** | base url for all links
**link** | link to external source
**style** | CSS inside HTML page
**script** | Javascript code
**meta** | metadata
**meta** *http-equiv*="refresh" *content*="10" | auto-refresh page in 10s


## Text content

### Headings
```html
<h1>Main heading</h1>
<!-- etc -->
<h6>Level-6 heading</h6>
```

tag | element
--- | ---
**h1** | main heading
**h6** | least important heading

### Paragraphs
```html
<p>Paragraph.<br/>
Other line.</p>
<p>Other paragraph.</p>
<hr/>
<p>See the line above.</p>
```

tag | element
--- | ---
**p** | paragraph
**br** | line break
**hr** | horizontal line

### Formatting
```html
<em>Formatting</em> is <strong>important</strong> !
(a+b)<sup>2</sup> = a<sup>2</sup> + b<sup>2</sup> + 2ab
```

tag | element
--- | ---
**sub** | subscript
**sup** | superscript
**em** | emphasize
**strong** | important
**mark** | highlighted
**small** | small
**i** | italic
**b** | bold

### Quotes
```html
<cite>This book</cite> was written by this author.
<q cite="url">quotation</q>
<blockquote cite="url">
Lorem ipsum<br/>
Lorem ipsum
</blockquote>
```

tag | element
--- | ---
**cite** | title of a work
**q** | inline quotation
**blockquote** | quotation


## Content

### Links
```html
<a href="url">link</a>
<a href="url" target=_blank>open in a new window</a>

<a href="#comments">watch comments</a>
<h2 id="comments">comments</h2>
```

tag | element
--- | ---
**a** | hyperlink

### Images
```html
<img src="image.png" alt="description" width="300" height="200" />
```

tag | element
--- | ---
**img** | image

### Blocks
```html
<div>block</div>
<span>inline</span>
```

tag | element
--- | ---
**div** | block-level element
**span** | inline element


## Lists

### Unordered list
```html
<ul>
    <li>item</li>
    <li>item</li>
    <li>item</li>
</ul>
```

tag | element
--- | ---
**ul** | unordered list
**li** | list item

### Ordored list
```html
<ol>
    <li>first</li>
    <li>second</li>
    <li>third</li>
</ol>
```

tag | element
--- | ---
**ol** | ordered list
**li** | list item

### Definition list
```html
<dl>
    <dt>term</dt><dd>definition</dd>
    <dt>term</dt><dd>definition</dd>
    <dt>term</dt><dd>definition</dd>
</dl>
```

tag | element
--- | ---
**dl** | definition list
**dt** | term
**dd** | definition


## Tables

### Basic table
```html
<table>
<tr>
    <th>heading 1</th>
    <th>heading 2</th>
</tr>
<tr>
    <td>line 1, column 1</td>
    <td>line 1, column 2</td>
</tr>
<tr>
    <td>line 2, column 1</td>
    <td>line 2, column 2</td>
</tr>
</table>
```

tag | element
--- | ---
**table** | table
**tr** | table row
**th** | table heading
**td** | table cell

### Advanced table
```html
<table>
<caption>caption</caption>
<colgroup>
    <col span="2" style="..." />
    <col style="..." />
</colgroup>
<thead>
    <tr>
        <th>heading 1</th>
        <th>heading 2</th>
        <th>heading 3</th>
    </tr>
</thead>
<tfoot>
    <tr>
        <th>footer 1</th>
        <th>footer 2</th>
        <th>footer 3</th>
    </tr>
</tfoot>
<tbody>
    <tr>
        <td>line 1, column 1</td>
        <td>line 1, column 2</td>
        <td>line 1, column 3</td>
    </tr>
    <tr>
        <td>line 2, column 1</td>
        <td>line 2, column 2</td>
        <td>line 2, column 3</td>
    </tr>
</tbody>
</table>
```

tag | element
--- | ---
**caption** | caption
**colgroup** | defines groups of columns
**col** | defines column's properties
**thead** | groups headings together
**tfoot** | groups footers together
**tbody** | groups other rows


## Forms
```html
<form action="url" method="post">
    <fieldset>
        <legend>Who are you ?</legend>
        <label>Login :<input type="text" name="login" /></label><br/>
        <label for="pswd">Password :</label><input type="password" name="password" id="pswd" /><br/>
        <input type="radio" name="sex" value="male" />Male<br/>
        <input type="radio" name="sex" value="female" />Female<br/>
    </fieldset>
    
    <label>Your favorite color : <select name="color">
        <option>red</option>
        <option>green</option>
        <option>blue</option>
    </select></label>
    
    <input type="checkbox" name="available" value="monday" />Monday<br/>
    <input type="checkbox" name="available" value="tuesday" />Tuesday<br/>
    
    <textarea name="comments" rows="10" cols="30" placeholder="Write your comments here"><textarea/>
    
    <input type="submit" value="Button text">
</form>
```

tag | element
--- | ---
**form** | form
**label** | label for input
**fieldset** | group inputs together
**legend** | legend for fieldset
**input** type="*text*" | text input
**input** type="*password*" | password input
**input** type="*radio*" | radio button
**input** type="*checkbox*" | checkbox
**input** type="*submit*" | send form
**select** | drop-down list
**option** | drop-down list item
**optgroup** | group of drop-down list items
**datalist** | autocompletion list
**textarea** | large text input


## HTML5 Semantic

### Page layout
```html
<header>My website</header>
<nav>
    <a href="page1">Page 1</a>
    <a href="page2">Page 2</a>
    <a href="page3">Page 3</a>
</nav>

<section>
    Hello everybody, Welcome to my website !
</section>

<article>
    <header>
        <h2>Title</h2>
    </header>
    <p>
        My article
    </p>
</article>

<aside>
    Writen by me
</aside>

<section id="comments">
    <article>Comment 1</article>
    <article>Comment 2</article>
</section>

<footer>
Copyright notice
</footer>
```

tag | element
--- | ---
**header** | header of document or section
**footer** | footer of document or section
**section** | section
**article** | article, forum post, blog post, comment
**aside** | aside content related to surrounding content
**nav** | navigation links

### New elements
```html
<figure>
    <img src="image.png" alt="figure 1" />
    <figcaption>Figure 1</figcaption>
</figure>

<details>
    <summary>Declaration of M. X on <time datetime="2013-12-25">Christmas day</time></summary>
    <p>M. X said...</p>
</details>

Downloading progress : <progress value="53" max="100"></progress>
Disk space : <meter value="62" min="10" max="350"></meter>
```

tag | element
--- | ---
**figure** | an illustration
**figcaption** | caption of a figure element
**details** | details that can be shown or hidden
**summary** | visible heading of a details element
**progress** | progress of a task
**meter** | display a gauge
**time** | machine-readable time indication