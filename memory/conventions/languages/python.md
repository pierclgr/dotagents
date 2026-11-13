# Python preferences

- Docstring style: Google
- Coding convention: PEP8
- Type hints: required everywhere (variables, arguments, parameters, object fields, class fields, returns, etc.), also trivial ones (int, float etc.) (PEP 484)
- Imports: at module top. Import inside a function or method only for a specific runtime need (e.g. the module must load where the package is not installed), and only when the module's other top-level imports don't already require that environment
