<!DOCTYPE html>
<html>
<head>
    <title>Results for "{{query}}"</title>
</head>
<body>

    <div style="text-align: right;">
        <p>{{loginStatus}}</p>
        <form action="{{actionURL}}" method="get"><button type="submit">{{buttonText}}</button></form>
    </div>

    <form action="/search" method="get">
        <img src="/static/EurekaLogo.jpg" alt="Euereka Logo" width="50" height="40">
        <input type="text" name="keywords" value="{{query}}">
        <input type="submit" value="Search">
    </form>

    <h2>Results for "{{query}}" (Page {{page}})</h2>

    % if not urls:
        <p>No results found.</p>
    % else:
        <ul>
            % for url, title, pr in urls:
                <p><a href="{{url}}">{{title}}</a> (Page rank: {{pr}})</p>
            % end
        </ul>
    % end

    <div style="margin-top:20px;">
        % if page > 1:
            <a href="/search?keywords={{query}}&page={{page-1}}">Previous</a>
        % end

        Page {{page}} of {{total_pages}}

        % if page < total_pages:
            <a href="/search?keywords={{query}}&page={{page+1}}">Next</a>
        % end
    </div>

    <p><a href="/">Back to Home</a></p>
</body>
</html>