<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{query}} - EUREKA! Search</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }

        .header {
            max-width: 900px;
            margin: 0 auto 30px auto;
            display: flex;
            align-items: center;
            gap: 20px;
        }

        .logo {
            font-size: 32px;
            font-weight: bold;
            color: #4285f4;
            text-decoration: none;
        }

        .search-box {
            flex: 1;
            display: flex;
            gap: 10px;
        }

        .search-box input[type="text"] {
            flex: 1;
            padding: 12px;
            font-size: 16px;
            border: 1px solid #ddd;
            border-radius: 4px;
        }

        .search-box button {
            padding: 12px 24px;
            background-color: #4285f4;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
        }

        .search-box button:hover {
            background-color: #357ae8;
        }

        .container {
            max-width: 900px;
            margin: 0 auto;
        }

        .stats {
            color: #70757a;
            font-size: 14px;
            margin-bottom: 20px;
        }

        .cache-badge {
            display: inline-block;
            padding: 2px 8px;
            background-color: #34a853;
            color: white;
            border-radius: 3px;
            font-size: 12px;
            margin-left: 10px;
        }

        .response-time {
            color: #5f6368;
            font-size: 13px;
            margin-left: 10px;
        }

        .result {
            background: white;
            padding: 20px;
            margin-bottom: 10px;
            border-radius: 8px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }

        .result-title {
            font-size: 20px;
            margin-bottom: 5px;
        }

        .result-title a {
            color: #1a0dab;
            text-decoration: none;
        }

        .result-title a:hover {
            text-decoration: underline;
        }

        .result-url {
            color: #006621;
            font-size: 14px;
            margin-bottom: 8px;
        }

        .result-snippet {
            color: #4d5156;
            font-size: 14px;
            line-height: 1.6;
        }

        .result-snippet b {
            font-weight: bold;
            color: #202124;
        }

        .result-meta {
            display: flex;
            gap: 15px;
            margin-top: 8px;
            font-size: 12px;
            color: #70757a;
        }

        .score-badge {
            display: inline-block;
            padding: 2px 6px;
            background-color: #e8f0fe;
            color: #1967d2;
            border-radius: 3px;
        }

        .pagination {
            display: flex;
            justify-content: center;
            gap: 10px;
            margin-top: 30px;
            padding: 20px 0;
        }

        .pagination a, .pagination span {
            padding: 8px 16px;
            background: white;
            border: 1px solid #ddd;
            border-radius: 4px;
            text-decoration: none;
            color: #1a0dab;
        }

        .pagination span {
            background-color: #4285f4;
            color: white;
            border-color: #4285f4;
        }

        .pagination a:hover {
            background-color: #f8f9fa;
        }

        .no-results {
            text-align: center;
            padding: 40px;
            background: white;
            border-radius: 8px;
        }

        .analytics-link {
            text-align: center;
            margin-top: 20px;
            font-size: 14px;
        }

        .analytics-link a {
            color: #4285f4;
            text-decoration: none;
        }

        .analytics-link a:hover {
            text-decoration: underline;
        }
    </style>
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
