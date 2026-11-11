# Planning

## Think before coding
**Don't assume. Don't hide confusion. Surface tradeoffs.** Before implementing:
- State assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them — don't pick silently.
- If simpler approach exists, say so. Push back when warranted.
- If unclear, stop. Name what's confusing. Ask.

When writing a plan, include:
1. **Class architecture blueprint**:
   - a Mermaid class diagram of the classes and their relations. Use the UML
     relations, each arrow with a short label that names the call or the role:
     - `<|--` inheritance: a class subclasses another.
     - `..|>` realization: a class implements an abstract base or interface.
     - `*--` composition: a class creates and owns the other.
     - `o--` aggregation: a class holds a shared object that it did not create.
     - `-->` association: a class keeps the other in a field and calls it.
     - `..>` dependency: a class uses or creates the other only inside a method.
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
   - in a change to existing code, the blueprint shows only what changes:
     new, changed and removed fields and methods, each marked `# NEW`,
     `# CHANGED` or `# REMOVED`. Leave out unchanged members. For a class
     that only moves to another file, write the move in one line, with no
     blueprint.
2. **Pseudocode**: pseudocode of the implementation, especially of the biggest methods, functions and code slices
