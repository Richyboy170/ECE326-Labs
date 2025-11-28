<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Analytics Dashboard - EUREKA!</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
        }

        .header {
            text-align: center;
            margin-bottom: 40px;
        }

        .header h1 {
            color: #4285f4;
            margin-bottom: 10px;
        }

        .back-link {
            color: #5f6368;
            text-decoration: none;
        }

        .back-link:hover {
            text-decoration: underline;
        }

        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }

        .card {
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }

        .card h2 {
            margin-top: 0;
            color: #202124;
            font-size: 18px;
            border-bottom: 2px solid #4285f4;
            padding-bottom: 10px;
        }

        .stat {
            display: flex;
            justify-content: space-between;
            padding: 10px 0;
            border-bottom: 1px solid #f0f0f0;
        }

        .stat:last-child {
            border-bottom: none;
        }

        .stat-label {
            color: #5f6368;
            font-size: 14px;
        }

        .stat-value {
            color: #202124;
            font-weight: bold;
            font-size: 16px;
        }

        .stat-value.good {
            color: #34a853;
        }

        .stat-value.warning {
            color: #fbbc04;
        }

        .stat-value.bad {
            color: #ea4335;
        }

        .query-list {
            list-style: none;
            padding: 0;
            margin: 0;
        }

        .query-item {
            padding: 12px 0;
            border-bottom: 1px solid #f0f0f0;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .query-item:last-child {
            border-bottom: none;
        }

        .query-text {
            color: #1a0dab;
            font-weight: 500;
        }

        .query-count {
            background-color: #e8f0fe;
            color: #1967d2;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 13px;
            font-weight: bold;
        }

        .query-meta {
            font-size: 12px;
            color: #70757a;
            margin-top: 4px;
        }

        .empty-state {
            text-align: center;
            padding: 40px;
            color: #70757a;
        }

        .metric-bar {
            height: 8px;
            background-color: #e8e8e8;
            border-radius: 4px;
            overflow: hidden;
            margin-top: 8px;
        }

        .metric-bar-fill {
            height: 100%;
            background-color: #4285f4;
            transition: width 0.3s ease;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Analytics Dashboard</h1>
            <a href="/" class="back-link">&larr; Back to Search</a>
        </div>

        <div class="grid">
            <div class="card">
                <h2>Performance (24h)</h2>
                <div class="stat">
                    <span class="stat-label">Total Queries</span>
                    <span class="stat-value">{{performance['total_queries']}}</span>
                </div>
                <div class="stat">
                    <span class="stat-label">Total Clicks</span>
                    <span class="stat-value">{{performance['total_clicks']}}</span>
                </div>
                <div class="stat">
                    <span class="stat-label">Click-Through Rate</span>
                    <span class="stat-value {{!'good' if performance['overall_ctr'] > 30 else 'warning' if performance['overall_ctr'] > 10 else 'bad'}}">
                        {{f"{performance['overall_ctr']:.1f}"}}%
                    </span>
                </div>
                <div class="stat">
                    <span class="stat-label">Avg Response Time</span>
                    <span class="stat-value {{!'good' if performance['avg_response_time_ms'] < 100 else 'warning' if performance['avg_response_time_ms'] < 500 else 'bad'}}">
                        {{f"{performance['avg_response_time_ms']:.1f}"}}ms
                    </span>
                </div>
                <div class="stat">
                    <span class="stat-label">Zero Result Rate</span>
                    <span class="stat-value {{!'bad' if performance['zero_result_rate'] > 20 else 'warning' if performance['zero_result_rate'] > 5 else 'good'}}">
                        {{f"{performance['zero_result_rate']:.1f}"}}%
                    </span>
                </div>
            </div>

            <div class="card">
                <h2>Cache Performance</h2>
                <div class="stat">
                    <span class="stat-label">Cache Size</span>
                    <span class="stat-value">{{cache_stats['size']}} / {{cache_stats['capacity']}}</span>
                </div>
                <div class="metric-bar">
                    <div class="metric-bar-fill" style="width: {{cache_stats['size'] / cache_stats['capacity'] * 100}}%"></div>
                </div>
                <div class="stat">
                    <span class="stat-label">Cache Hits</span>
                    <span class="stat-value good">{{cache_stats['hits']}}</span>
                </div>
                <div class="stat">
                    <span class="stat-label">Cache Misses</span>
                    <span class="stat-value">{{cache_stats['misses']}}</span>
                </div>
                <div class="stat">
                    <span class="stat-label">Hit Rate</span>
                    <span class="stat-value {{!'good' if cache_stats['hit_rate'] > 50 else 'warning' if cache_stats['hit_rate'] > 20 else 'bad'}}">
                        {{f"{cache_stats['hit_rate']:.1f}"}}%
                    </span>
                </div>
                <div class="stat">
                    <span class="stat-label">Evictions</span>
                    <span class="stat-value">{{cache_stats['evictions']}}</span>
                </div>
            </div>
        </div>

        <div class="grid">
            <div class="card">
                <h2>Popular Queries</h2>
                % if len(popular) > 0:
                    <ul class="query-list">
                        % for query, count, ctr in popular:
                            <li class="query-item">
                                <div>
                                    <div class="query-text">{{query}}</div>
                                    <div class="query-meta">CTR: {{f'{ctr*100:.1f}'}}%</div>
                                </div>
                                <span class="query-count">{{count}}</span>
                            </li>
                        % end
                    </ul>
                % else:
                    <div class="empty-state">No queries yet</div>
                % end
            </div>

            <div class="card">
                <h2>Recent Queries (24h)</h2>
                % if len(recent) > 0:
                    <ul class="query-list">
                        % for query, timestamp, num_results in recent[:10]:
                            <li class="query-item">
                                <div>
                                    <div class="query-text">{{query}}</div>
                                    <div class="query-meta">{{timestamp}} - {{num_results}} results</div>
                                </div>
                            </li>
                        % end
                    </ul>
                % else:
                    <div class="empty-state">No recent queries</div>
                % end
            </div>
        </div>
    </div>
</body>
</html>
