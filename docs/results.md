# Wyniki wykonania testów

- **Data:** 2026-11-07, środowisko lokalne: Windows 11, Python 3.11.9, Selenium 4.50.0,
  Chrome 157 (headless), Edge; Gitea 28.3.0 w Dockerze (WSL2 Debian).
- **Polecenie:** `SCREENSHOTS=all pytest --junitxml=reports/junit.xml --html=reports/report.html --self-contained-html --durations=0`
- **Czas całkowity:** 109,9 s

## Podsumowanie

| Grupa | Wykonania | Zaliczone | Niezaliczone | Oczekiwane niepowodzenie (xfail) | Czas [s] |
|---|---|---|---|---|---|
| Testy dymne | 2 | 2 | 0 | 0 | 3,3 |
| UI Selenium (TC-F01–F12) | 13 | 13 | 0 | 0 | 52,3 |
| API (TC-F13–F17) | 13 | 13 | 0 | 0 | 4,2 |
| Niefunkcjonalne (TC-NF01–NF05) | 10 | 8 | 1 | 1 | 49,2 |
| **Razem** | **38** | **36** | **1** | **1** | **109,9** |

Wykonania > przypadków testowych, bo część przypadków jest sparametryzowana
(TC-F02: 2 wartości brzegowe, TC-F14: 6 reguł tablicy decyzyjnej, TC-F17: 4 warianty tokena,
TC-NF04: 5 kontroli, TC-NF05: 2 przeglądarki).

## Wyniki per przypadek testowy

| ID | Wynik | Czas [s] | Uwagi |
|---|---|---|---|
| TC-F01 | Zaliczony | 3,45 | |
| TC-F02 | Zaliczony (2/2) | 7,02 | 7 znaków odrzucone, 8 zaakceptowane |
| TC-F03 | Zaliczony | 3,33 | |
| TC-F04 | Zaliczony | 3,31 | |
| TC-F05 | Zaliczony | 3,82 | |
| TC-F06 | Zaliczony | 3,70 | |
| TC-F07 | Zaliczony | 4,54 | |
| TC-F08 | Zaliczony | 5,68 | wcześniej niestabilny – poprawiony w kodzie testu (StaleElementReference) |
| TC-F09 | Zaliczony | 5,00 | |
| TC-F10 | Zaliczony | 5,13 | |
| TC-F11 | Zaliczony | 3,91 | |
| TC-F12 | Zaliczony | 3,39 | |
| TC-F13 | Zaliczony | 0,42 | |
| TC-F14 | Zaliczony (6/6) | 2,38 | |
| TC-F15 | Zaliczony | 0,52 | |
| TC-F16 | Zaliczony | 0,54 | |
| TC-F17 | Zaliczony (4/4) | 0,34 | |
| TC-NF01 | Zaliczony | 32,00 | p95 zagregowane 32 ms (limit 500 ms), 19,0 żądań/s, 0% błędów |
| TC-NF02 | Zaliczony | 4,17 | mediany 23–40 ms (limit 2000 ms) |
| TC-NF03 | **Niezaliczony** | 4,32 | DEF-02 – krytyczne naruszenia WCAG na 5/5 widokach |
| TC-NF04 | Zaliczony (4/4) + 1 xfail | 0,49 | DEF-01 – login CSRF (znany defekt) |
| TC-NF05 | Zaliczony (2/2) | 8,25 | Chrome, Edge |

## Wydajność – TC-NF01 (Locust, 20 użytkowników, narastanie 5/s, 30 s)

| Żądanie | p50 [ms] | p95 [ms] | żądania/s |
|---|---|---|---|
| API repo | 14 | 23 | 5,1 |
| API issues | 23 | 31 | 4,9 |
| API search | 15 | 22 | 2,8 |
| WEB /{owner}/{repo} | 22 | 42 | 4,0 |
| WEB /explore/repos | 3 | 6 | 2,2 |
| **Zagregowane** | **20** | **32** | **19,0** |

## Czas ładowania stron – TC-NF02 (mediana z 3 pomiarów, `loadEventEnd`)

| Strona | Czas [ms] |
|---|---|
| `/` | 24,6 |
| `/explore/repos` | 22,9 |
| `/{owner}/{repo}` | 40,4 |
| `/{owner}/{repo}/issues` | 35,1 |
| `/user/settings` | 23,9 |

## CI (GitHub Actions)

Run #1 (PR #18): job funkcjonalny zaliczony (1 min 9 s), job niefunkcjonalny niezaliczony wyłącznie
przez TC-NF03 (DEF-02) – job ma `continue-on-error`, więc całość ma status *Success*.

## Defekty

Zob. [defects.md](defects.md): DEF-01 (login CSRF), DEF-02 (WCAG), OBS-01 (brak CSP), OBS-02 (kontrast).
