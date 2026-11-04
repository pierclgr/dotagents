# Planning

## Think before coding
**Don't assume. Don't hide confusion. Surface tradeoffs.** Before implementing:
- State assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them — don't pick silently.
- If simpler approach exists, say so. Push back when warranted.
- If unclear, stop. Name what's confusing. Ask.

When writing a plan, include:
1. **Class architecture blueprint**:
   - a Mermaid class diagram of the classes and their relations.
   - a blueprint of each class: fields and method signatures, with no
     implementation. Each class, field, method and has a short 
     description of what it holds or does. Example:
     ```python
     # class representing a person
     class Person:
         name: str  # first name of the person
         surname: str  # last name of the person
         birth: date  # date of birth

         @property
         def age(self) -> int: ...  # age in years, computed from birth
     ```
2. **Pseudocode**: pseudocode of the implementation, especially of the biggest methods, functions and code slices
