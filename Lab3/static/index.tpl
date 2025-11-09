<!DOCTYPE html>
<html lang="en">

<head>
  <meta charset="UTF-8">
  <title>EUREKA!</title>
</head>

<div style="text-align: right;">
  <p>{{loginStatus}}</p>
  <form action="{{actionURL}}" method="get"><button type="submit">{{buttonText}}</button></form>
</div>

<body style="text-align: center;">
  <img src="/static/EurekaLogo.jpg" alt="Euereka Logo" width="150" height="120">
  <h1>
    EUREKA!
  </h1>
  <form action="/search" method="get">
    <label>
      Search:
      <input name="keywords" type="text" />
    </label>
    <input value="Submit" type="submit" />
  </form>
</body>

</html>