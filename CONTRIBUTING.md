# Contributing to ThreatFeed

We love contributions! Here's how you can help.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/yourusername/threatfeed-mcp.git`
3. Create a branch: `git checkout -b feature/amazing-feature`
4. Set up development environment:
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

## Development

### Running Tests

```bash
python -m pytest tests/
```

### Code Style

Follow PEP 8:
```bash
pip install flake8
flake8 src/
```

### Adding New Threat Sources

1. Create a new source class in `src/sources/`:

```python
from sources.rss_sources import RSSSource

class MySource(RSSSource):
    def __init__(self):
        super().__init__(
            name="My Source",
            url="https://example.com/feed"
        )
```

2. Add to `THREAT_SOURCES` in `src/sources/rss_sources.py`

3. Test it:
```python
from sources.rss_sources import THREAT_SOURCES
source = THREAT_SOURCES['my_source']
threats = source.fetch()
```

### Adding New MCP Tools

1. Add handler in `src/mcp_server.py`:

```python
def my_tool(param1: str = None) -> MCPToolResponse:
    """Tool description."""
    try:
        # Implementation
        result = agg.search_threats(keywords=param1)
        return MCPToolResponse(success=True, data=[...])
    except Exception as e:
        return MCPToolResponse(success=False, error=str(e))
```

2. Register in `TOOLS` dict:

```python
TOOLS["my_tool"] = {
    "description": "Tool description",
    "parameters": {
        "param1": {"type": "string", "description": "Parameter"}
    },
    "handler": my_tool
}
```

3. Test with interactive mode:
```bash
python src/mcp_server.py --interactive
>> my_tool param1=value
```

## Documentation

Update docs when making changes:
- `docs/ARCHITECTURE.md` - System design changes
- `docs/MCP_INTEGRATION.md` - MCP tool changes
- `docs/DEPLOYMENT.md` - Deployment changes
- `README.md` - User-facing changes

## Pull Request Process

1. Update documentation
2. Add tests for new functionality
3. Run tests: `pytest tests/`
4. Check code style: `flake8 src/`
5. Submit PR with:
   - Clear title and description
   - Reference to any related issues
   - Screenshot/demo if UI changes

## Reporting Issues

Use GitHub Issues with:
- Clear title
- Detailed description
- Steps to reproduce
- Environment (OS, Python version)
- Expected vs actual behavior

## Feature Requests

Open a GitHub Discussion or Issue with:
- Use case description
- Why it's needed
- Proposed implementation (optional)

## Code of Conduct

Be respectful and inclusive. We don't tolerate harassment or discrimination.

## Questions?

- 📖 Read [docs/](docs/)
- 💬 Join [Discussions](https://github.com/yourusername/threatfeed-mcp/discussions)
- 📧 Email maintainers

## License

By contributing, you agree your code will be licensed under the MIT License.

Thanks for helping make ThreatFeed better! 🛡️
