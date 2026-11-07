# Rejestr defektów i obserwacji

Przedmiot testów: Gitea 28.3.0 (obraz `gitea/gitea:28.3.0`, SQLite), środowisko lokalne.

| ID | Tytuł | Wykryty przez | Ważność | Priorytet | Status |
|---|---|---|---|---|---|
| DEF-01 | Formularz logowania akceptuje żądania cross-site (login CSRF) | TC-NF04 | Niska | Niski | Otwarty |
| DEF-02 | Krytyczne naruszenia WCAG 2.1 AA na kluczowych widokach | TC-NF03 | Średnia | Średni | Otwarty |
| OBS-01 | Brak nagłówka `Content-Security-Policy` | TC-NF04 | – | – | Obserwacja |
| OBS-02 | Niewystarczający kontrast tekstu (axe `color-contrast`, serious) | TC-NF03 | – | – | Obserwacja |

## DEF-01 – login CSRF
- **Kroki:** `POST /user/login` z nagłówkami `Origin: http://evil.example`, `Sec-Fetch-Site: cross-site` i poprawnymi danymi.
- **Oczekiwany rezultat:** odrzucenie żądania (403), tak jak dla innych akcji zmieniających stan (`/repo/create` zwraca 403).
- **Rzeczywisty rezultat:** `303 -> /`, ustawiona sesja zalogowanego użytkownika.
- **Wpływ:** atakujący może zalogować ofiarę na swoje konto (session fixation / login CSRF).
- **Automatyzacja:** `tests/nonfunctional/test_quality.py::TestSecurity::test_cross_origin_login_is_rejected` (`xfail strict`).

## DEF-02 – dostępność (axe-core 4.10.2, reguły wcag2a/wcag2aa/wcag21aa)
| Widok | Krytyczne | Poważne (serious) |
|---|---|---|
| `/user/login` | aria-required-children (2) | color-contrast (4) |
| `/user/sign_up` | aria-required-children (2) | color-contrast (4) |
| `/{owner}/{repo}` | aria-required-children (3), button-name (1) | aria-prohibited-attr, color-contrast, link-name |
| `/{owner}/{repo}/issues` | aria-required-children (4) | aria-prohibited-attr, color-contrast (8) |
| `/repo/create` | aria-required-children (2), label (4) | aria-input-field-name (3), color-contrast, link-in-text-block |

- **Oczekiwany rezultat (kryterium TC-NF03):** brak naruszeń o wpływie `critical`.
- **Wpływ:** użytkownicy czytników ekranu nie otrzymują poprawnej struktury menu (role `menu` bez wymaganych dzieci), pola formularza nowego repo bez etykiet, przycisk bez nazwy dostępnej.
- Pełne dane: `reports/axe.json` (generowany przy każdym przebiegu).
