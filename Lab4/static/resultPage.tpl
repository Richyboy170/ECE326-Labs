<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{query}} - EUREKA! Search</title>
    <link rel="stylesheet" href="static/resultPageStyle.css">
</head>
<body>
    <div class="header">
        <a href="/" class="logo">EUREKA!</a>
        <form class="search-box" action="/search" method="get">
            <input type="text" name="keywords" value="{{query}}" placeholder="Enter search query..." autofocus>
            <button type="submit">Search</button>
        </form>
    </div>

    <div class="container">
        <div class="stats">
            About {{len(urls) if page == 1 else '?'}} results
            % if cache_hit:
                <span class="cache-badge">CACHED</span>
            % end
            <span class="response-time">{{response_time}}</span>
        </div>

        % if len(urls) == 0:
            <div class="no-results">
                <h2>No results found for "{{query}}"</h2>
                <p>Try different keywords or check your spelling</p>
            </div>
        % else:
            % for url, title, score, pagerank, snippet in urls:
                <div class="result">
                    <div class="result-title">
                        <a href="{{url}}" target="_blank">{{title or url}}</a>
                    </div>
                    <div class="result-url">{{url}}</div>
                    <div class="result-snippet">{{!snippet}}</div>
                    <div class="result-meta">
                        <span class="score-badge">Relevance: {{f'{score:.3f}'}}</span>
                        <span>PageRank: {{f'{pagerank:.3f}'}}</span>
                    </div>
                </div>
            % end

            <div class="pagination">
                % if page > 1:
                    <a href="/search?keywords={{query}}&page=1">&laquo; First</a>
                    <a href="/search?keywords={{query}}&page={{page-1}}">&lt; Prev</a>
                % end

                % for p in range(max(1, page-2), min(total_pages+1, page+3)):
                    % if p == page:
                        <span>{{p}}</span>
                    % else:
                        <a href="/search?keywords={{query}}&page={{p}}">{{p}}</a>
                    % end
                % end

                % if page < total_pages:
                    <a href="/search?keywords={{query}}&page={{page+1}}">Next &gt;</a>
                    <a href="/search?keywords={{query}}&page={{total_pages}}">Last &raquo;</a>
                % end
            </div>
        % end

        <div class="analytics-link">
            <a href="/analytics">View Analytics Dashboard</a>
        </div>
    </div>
</body>
</html>
