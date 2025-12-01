<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>EUREKA! Search Engine</title>
    <link rel="stylesheet" href="static/indexStyle.css">
</head>
<body>
    <div class="container">
        <div class="Logo">
            <img src="/static/eurekaLogo.png" alt="Euereka Logo" width="150" height="120">
        </div>
        <h1>EUREKA!</h1>
        <form action="/search" method="GET" class="search-box">
            <input type="text" name="keywords" placeholder="Enter search keyword..." required autofocus>
            <button type="submit">Search</button>
        </form>
        <div class="info">
            <p>Enter a keyword to search indexed documents</p>
        </div>
        {{!STATS}}
    </div>
</body>
</html>