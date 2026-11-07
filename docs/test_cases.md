# Przypadki testowe

Przedmiot testów: Gitea 28.3.0. Podstawa testów: analiza produktu ([features.md](features.md)),
dokumentacja Gitea i REST API (`/api/swagger`), norma ISO/IEC 25010:2023, WCAG 2.1/2.2.
Dane wspólne: konto administratora `admin` (zakłada użytkowników testowych przez API),
użytkownik testowy tworzony automatycznie (`user-<losowy>` / `Test123!pass`), środowisko
z `docker-compose.yml`. Każdy test sprząta utworzone dane (warunek końcowy domyślny:
brak pozostawionych danych testowych, chyba że zaznaczono inaczej).

Implementacja: `tests/ui/test_auth_repo.py` (F01–F06), `tests/ui/test_issues_pr.py` (F07–F12),
`tests/api/test_api.py` (F13–F17), `tests/nonfunctional/` (NF01–NF05). ID przypadku jest
w markerze `@pytest.mark.tc`, powiązane funkcje w `@pytest.mark.feature`.

---

## Przypadki funkcjonalne

### TC-F01 – Rejestracja konta poprawnymi danymi
| Pole | Wartość |
|---|---|
| Priorytet | Wysoki |
| Technika | Podział na klasy równoważności (klasa poprawna: unikalna nazwa, poprawny e-mail, hasło ≥ 8 znaków) |
| Typ testu | Funkcjonalny |
| Poziom testu | Testowanie systemowe (UI, Selenium) |
| Warunki wstępne / dane | Rejestracja włączona; nazwa `reg-<losowy>`, e-mail `<nazwa>@example.com`, hasło `Valid123!pass`; użytkownik niezalogowany |
| Powiązane funkcje | F01 |

| # | Krok | Oczekiwany rezultat |
|---|---|---|
| 1 | Otwórz `/user/sign_up` | Widoczny formularz z polami: nazwa, e-mail, hasło, powtórz hasło |
| 2 | Wypełnij pola danymi testowymi | Pola przyjmują wartości, brak komunikatów walidacji |
| 3 | Kliknij „Register Account” | Przekierowanie na stronę główną; w nawigacji awatar z nazwą nowego użytkownika |
| 4 | Sprawdź `GET /api/v1/users/<nazwa>` | HTTP 200 |

Warunki końcowe: konto istnieje i jest aktywne, użytkownik zalogowany; po teście konto usunięte przez administratora.

### TC-F02 – Walidacja minimalnej długości hasła przy rejestracji
| Pole | Wartość |
|---|---|
| Priorytet | Wysoki |
| Technika | Analiza wartości brzegowych (dwupunktowa: 7 i 8 znaków; granica `MIN_PASSWORD_LENGTH = 8`) |
| Typ testu | Funkcjonalny |
| Poziom testu | Testowanie systemowe (UI, Selenium) |
| Warunki wstępne / dane | Użytkownik niezalogowany; hasło `Ab1!Ab1` (7 zn.) oraz `Ab1!Ab1!` (8 zn.) |
| Powiązane funkcje | F01 |

| # | Krok | Oczekiwany rezultat |
|---|---|---|
| 1 | Otwórz `/user/sign_up`, wypełnij formularz hasłem 7-znakowym, wyślij | Komunikat „Password length cannot be less than 8 characters.”; brak przekierowania |
| 2 | Sprawdź `GET /api/v1/users/<nazwa>` | HTTP 404 – konto nie powstało |
| 3 | Powtórz krok 1 z hasłem 8-znakowym (nowa nazwa) | Konto utworzone, użytkownik zalogowany (awatar w nawigacji) |

Warunki końcowe: istnieje wyłącznie konto z hasłem 8-znakowym; usunięte po teście.

### TC-F03 – Logowanie poprawnymi danymi
| Pole | Wartość |
|---|---|
| Priorytet | Wysoki |
| Technika | Podział na klasy równoważności (klasa poprawna) |
| Typ testu | Funkcjonalny |
| Poziom testu | Testowanie systemowe (UI, Selenium) |
| Warunki wstępne / dane | Istnieje aktywny użytkownik testowy; przeglądarka bez sesji |
| Powiązane funkcje | F02 |

| # | Krok | Oczekiwany rezultat |
|---|---|---|
| 1 | Otwórz `/user/login` | Formularz z polami nazwy i hasła |
| 2 | Wpisz poprawną nazwę i hasło, kliknij „Sign In” | Przekierowanie na `/` |
| 3 | Sprawdź nawigację | Awatar z tytułem równym nazwie użytkownika |

Warunki końcowe: aktywna sesja użytkownika testowego.

### TC-F04 – Odrzucenie logowania z błędnym hasłem
| Pole | Wartość |
|---|---|
| Priorytet | Wysoki |
| Technika | Podział na klasy równoważności (klasa niepoprawna: błędne hasło) |
| Typ testu | Funkcjonalny |
| Poziom testu | Testowanie systemowe (UI, Selenium) |
| Warunki wstępne / dane | Istnieje użytkownik testowy; hasło `wrong-password` |
| Powiązane funkcje | F02 |

| # | Krok | Oczekiwany rezultat |
|---|---|---|
| 1 | Otwórz `/user/login` | Formularz logowania |
| 2 | Wpisz poprawną nazwę i błędne hasło, wyślij | Komunikat „Username or password is incorrect.” |
| 3 | Sprawdź URL i nawigację | URL zawiera `/user/login`; brak awatara (użytkownik niezalogowany) |

Warunki końcowe: brak sesji; konto nie zostało zablokowane.

### TC-F05 – Utworzenie repozytorium z plikiem README
| Pole | Wartość |
|---|---|
| Priorytet | Wysoki |
| Technika | Podział na klasy równoważności (poprawna nazwa, repo publiczne, inicjalizacja włączona) |
| Typ testu | Funkcjonalny |
| Poziom testu | Testowanie systemowe (UI, Selenium + weryfikacja API) |
| Warunki wstępne / dane | Zalogowany użytkownik testowy; nazwa `ui-repo-<losowy>`, opis „Repository from a Selenium test” |
| Powiązane funkcje | F03, F04 |

| # | Krok | Oczekiwany rezultat |
|---|---|---|
| 1 | Otwórz `/repo/create` | Formularz nowego repozytorium |
| 2 | Podaj nazwę i opis, zaznacz „Initialize Repository”, kliknij „Create Repository” | Przekierowanie na `/<użytkownik>/<nazwa>` |
| 3 | Sprawdź listę plików | Lista zawiera `README.md` |
| 4 | Sprawdź sekcję README | Zawiera nazwę repo i opis |
| 5 | `GET /api/v1/repos/<użytkownik>/<nazwa>` | `description` = opis, `private` = false |

Warunki końcowe: repozytorium istnieje z jednym commitem; usunięte po teście.

### TC-F06 – Odrzucenie duplikatu nazwy repozytorium
| Pole | Wartość |
|---|---|
| Priorytet | Średni |
| Technika | Zgadywanie błędów (error guessing) |
| Typ testu | Funkcjonalny |
| Poziom testu | Testowanie systemowe (UI, Selenium) |
| Warunki wstępne / dane | Zalogowany użytkownik; istnieje jego repozytorium o nazwie X (utworzone przez API) |
| Powiązane funkcje | F03 |

| # | Krok | Oczekiwany rezultat |
|---|---|---|
| 1 | Otwórz `/repo/create`, podaj nazwę X, wyślij | Komunikat „The repository name is already used.” |
| 2 | Sprawdź URL | Pozostaje `/repo/create` |
| 3 | `GET /api/v1/user/repos` | Nazwa X występuje dokładnie raz |

Warunki końcowe: stan repozytoriów użytkownika bez zmian.

### TC-F07 – Utworzenie zgłoszenia z etykietą
| Pole | Wartość |
|---|---|
| Priorytet | Wysoki |
| Technika | Testowanie oparte na kryteriach akceptacji |
| Typ testu | Funkcjonalny |
| Poziom testu | Testowanie systemowe (UI, Selenium + weryfikacja API) |
| Warunki wstępne / dane | Zalogowany właściciel repozytorium; w repo istnieje etykieta `bug`; tytuł „Login error-<losowy>” |
| Powiązane funkcje | F05, F09 |

| # | Krok | Oczekiwany rezultat |
|---|---|---|
| 1 | Otwórz `/<repo>/issues/new` | Formularz z polem tytułu, opisem i panelem bocznym |
| 2 | Wpisz tytuł i opis | Wartości widoczne w polach |
| 3 | W panelu „Labels” wybierz `bug`, zamknij listę | Etykieta `bug` widoczna w panelu |
| 4 | Kliknij „Create Issue” | Przekierowanie na `/<repo>/issues/<n>`; tytuł i etykieta `bug` widoczne |
| 5 | `GET /api/v1/repos/<repo>/issues/<n>` | `state` = open, `labels` = [`bug`] |

Warunki końcowe: w repo istnieje 1 otwarte zgłoszenie z etykietą `bug`.

### TC-F08 – Komentarz, zamknięcie i ponowne otwarcie zgłoszenia
| Pole | Wartość |
|---|---|
| Priorytet | Wysoki |
| Technika | Testowanie przejść między stanami (open → closed → open; przejścia „zamknij z komentarzem”, „otwórz ponownie”) |
| Typ testu | Funkcjonalny |
| Poziom testu | Testowanie systemowe (UI, Selenium + weryfikacja API) |
| Warunki wstępne / dane | Zalogowany właściciel; otwarte zgłoszenie „To be closed” utworzone przez API |
| Powiązane funkcje | F05 |

| # | Krok | Oczekiwany rezultat |
|---|---|---|
| 1 | Otwórz stronę zgłoszenia | Przycisk statusu „Close Issue” |
| 2 | Dodaj komentarz „Bug confirmed” | Komentarz widoczny na osi czasu; stan nadal open |
| 3 | Wpisz „Fixed” i kliknij „Close with Comment” | Stan w API = closed; przycisk zmienia się na „Reopen Issue” |
| 4 | Kliknij „Reopen Issue” | Stan w API = open |
| 5 | `GET .../issues/<n>/comments` | Dokładnie 2 komentarze w kolejności: „Bug confirmed”, „Fixed” |

Warunki końcowe: zgłoszenie otwarte, 2 komentarze, 2 zdarzenia zmiany stanu na osi czasu.

### TC-F09 – Edycja pliku w edytorze przeglądarkowym i commit
| Pole | Wartość |
|---|---|
| Priorytet | Średni |
| Technika | Testowanie oparte na kryteriach akceptacji |
| Typ testu | Funkcjonalny |
| Poziom testu | Testowanie systemowe (UI, Selenium + weryfikacja API) |
| Warunki wstępne / dane | Zalogowany właściciel repo z `README.md`; nowa treść „Content changed in the editor”; opis commita „Update README from the UI” |
| Powiązane funkcje | F08, F04 |

| # | Krok | Oczekiwany rezultat |
|---|---|---|
| 1 | Otwórz `/<repo>/_edit/main/README.md` | Edytor kodu z bieżącą treścią pliku |
| 2 | Zaznacz całą treść i zastąp nową | Edytor zawiera wyłącznie nową treść |
| 3 | Wpisz opis commita, wybierz „Commit directly”, kliknij „Commit Changes” | Przekierowanie do widoku pliku `/src/branch/main/...` |
| 4 | `GET .../contents/README.md` | Zdekodowana treść = nowa treść |
| 5 | `GET .../commits?limit=1` | Wiadomość ostatniego commita = podany opis |

Warunki końcowe: gałąź `main` ma nowy commit ze zmienionym README.

### TC-F10 – Utworzenie i scalenie pull requesta
| Pole | Wartość |
|---|---|
| Priorytet | Wysoki |
| Technika | Testowanie oparte na kryteriach akceptacji (przepływ end-to-end) |
| Typ testu | Funkcjonalny |
| Poziom testu | Testowanie systemowe (UI, Selenium + weryfikacja API) |
| Warunki wstępne / dane | Zalogowany właściciel; gałąź `feature-x` z plikiem `feature.txt` (utworzona przez API); tytuł PR „Add feature.txt” |
| Powiązane funkcje | F06 |

| # | Krok | Oczekiwany rezultat |
|---|---|---|
| 1 | Otwórz `/<repo>/compare/main...feature-x` | Diff z 1 zmienionym plikiem, przycisk „New Pull Request” |
| 2 | Kliknij „New Pull Request”, wpisz tytuł, „Create Pull Request” | Przekierowanie na `/<repo>/pulls/<n>` |
| 3 | Kliknij „Create merge commit” i potwierdź | Etykieta stanu „Merged” |
| 4 | `GET .../pulls/<n>` | `merged` = true |
| 5 | `GET .../contents/feature.txt?ref=main` | HTTP 200 – plik w `main` |

Warunki końcowe: PR scalony i zamknięty, `main` zawiera `feature.txt`.

### TC-F11 – Wyszukiwanie repozytorium po nazwie
| Pole | Wartość |
|---|---|
| Priorytet | Średni |
| Technika | Podział na klasy równoważności (repo pasujące / niepasujące do frazy) |
| Typ testu | Funkcjonalny |
| Poziom testu | Testowanie systemowe (UI, Selenium) |
| Warunki wstępne / dane | Zalogowany użytkownik; repo `szukaj-<losowy>-app` oraz repo o niepasującej nazwie |
| Powiązane funkcje | F10 |

| # | Krok | Oczekiwany rezultat |
|---|---|---|
| 1 | Otwórz `/explore/repos` | Pole wyszukiwania i lista repozytoriów |
| 2 | Wpisz frazę `szukaj-<losowy>`, Enter | URL zawiera `q=` |
| 3 | Odczytaj wyniki | Repo pasujące jest na liście, repo niepasujące – nie |

Warunki końcowe: brak zmian danych (oba repo usunięte po teście).

### TC-F12 – Wylogowanie blokuje dostęp do ustawień konta
| Pole | Wartość |
|---|---|
| Priorytet | Wysoki |
| Technika | Testowanie przejść między stanami (zalogowany → niezalogowany) |
| Typ testu | Funkcjonalny |
| Poziom testu | Testowanie systemowe (UI, Selenium) |
| Warunki wstępne / dane | Zalogowany użytkownik testowy |
| Powiązane funkcje | F02, F07 |

| # | Krok | Oczekiwany rezultat |
|---|---|---|
| 1 | Otwórz menu awatara, kliknij „Sign Out” | W nawigacji link „Sign In”, brak awatara |
| 2 | Otwórz `/user/settings` | Przekierowanie na `/user/login?redirect_to=%2Fuser%2Fsettings` |

Warunki końcowe: brak aktywnej sesji.

### TC-F13 – CRUD repozytorium przez REST API
| Pole | Wartość |
|---|---|
| Priorytet | Wysoki |
| Technika | Testowanie oparte na kryteriach akceptacji (cykl życia zasobu) |
| Typ testu | Funkcjonalny |
| Poziom testu | Testowanie systemowe (REST API) |
| Warunki wstępne / dane | Użytkownik testowy z uwierzytelnieniem Basic; nazwa `crud-<losowy>` |
| Powiązane funkcje | F03 |

| # | Krok | Oczekiwany rezultat |
|---|---|---|
| 1 | `POST /user/repos` z opisem „v1” | 201; `full_name` = `<user>/<nazwa>` |
| 2 | `GET /repos/<user>/<nazwa>` | 200; `description` = „v1” |
| 3 | `PATCH` z `description` „v2”, `has_wiki` false | 200; pola zaktualizowane |
| 4 | `DELETE /repos/<user>/<nazwa>` | 204 |
| 5 | `GET /repos/<user>/<nazwa>` | 404 |

Warunki końcowe: repozytorium nie istnieje.

### TC-F14 – Widoczność repozytorium wg roli (tablica decyzyjna)
| Pole | Wartość |
|---|---|
| Priorytet | Wysoki |
| Technika | Testowanie z użyciem tablicy decyzyjnej (warunki: widoczność × rola; akcja: kod HTTP) |
| Typ testu | Funkcjonalny (bezpieczeństwo – kontrola dostępu) |
| Poziom testu | Testowanie systemowe (REST API) |
| Warunki wstępne / dane | Właściciel, drugi użytkownik, klient anonimowy; repo publiczne lub prywatne utworzone dla każdej reguły |
| Powiązane funkcje | F07 |

Tablica decyzyjna (6 reguł, każda to osobne wykonanie):

| Reguła | R1 | R2 | R3 | R4 | R5 | R6 |
|---|---|---|---|---|---|---|
| Repo prywatne | N | N | N | T | T | T |
| Rola | właściciel | inny | anonim | właściciel | inny | anonim |
| **Oczekiwany kod `GET /repos/...`** | 200 | 200 | 200 | 200 | **404** | **404** |

| # | Krok | Oczekiwany rezultat |
|---|---|---|
| 1 | Utwórz repo o widoczności z reguły | 201 |
| 2 | Wykonaj `GET /repos/<repo>` jako rola z reguły | Kod zgodny z tablicą |

Warunki końcowe: repozytorium usunięte; repo prywatne nie ujawniło swojego istnienia (404, nie 403).

### TC-F15 – Nadanie i odebranie dostępu kolaboratorowi
| Pole | Wartość |
|---|---|
| Priorytet | Wysoki |
| Technika | Testowanie przejść między stanami (brak dostępu → zapis → brak dostępu) |
| Typ testu | Funkcjonalny |
| Poziom testu | Testowanie systemowe (REST API) |
| Warunki wstępne / dane | Prywatne repo właściciela; drugi użytkownik |
| Powiązane funkcje | F07 |

| # | Krok | Oczekiwany rezultat |
|---|---|---|
| 1 | Drugi użytkownik: `GET /repos/<repo>` | 404 |
| 2 | Właściciel: `PUT /repos/<repo>/collaborators/<drugi>` z `permission: write` | 204 |
| 3 | Drugi użytkownik: `GET /repos/<repo>` | 200 |
| 4 | Drugi użytkownik: `POST /repos/<repo>/issues` | 201 – uprawnienie zapisu działa |
| 5 | Właściciel: `DELETE .../collaborators/<drugi>`; drugi: `GET` | 404 |

Warunki końcowe: drugi użytkownik nie ma dostępu; repo usunięte.

### TC-F16 – Licznik postępu kamienia milowego
| Pole | Wartość |
|---|---|
| Priorytet | Średni |
| Technika | Testowanie oparte na kryteriach akceptacji |
| Typ testu | Funkcjonalny |
| Poziom testu | Testowanie systemowe (REST API) |
| Warunki wstępne / dane | Repo użytkownika; milestone „v1.0”; 2 zgłoszenia przypisane do milestone |
| Powiązane funkcje | F09, F05 |

| # | Krok | Oczekiwany rezultat |
|---|---|---|
| 1 | Utwórz milestone i 2 zgłoszenia z `milestone` | 201 dla każdego |
| 2 | `GET /milestones/<id>` | `open_issues` = 2, `closed_issues` = 0 |
| 3 | Zamknij jedno zgłoszenie (`PATCH state=closed`) | 201 |
| 4 | `GET /milestones/<id>` | `open_issues` = 1, `closed_issues` = 1 |

Warunki końcowe: milestone z postępem 50%.

### TC-F17 – Uwierzytelnianie tokenem API
| Pole | Wartość |
|---|---|
| Priorytet | Średni |
| Technika | Podział na klasy równoważności (token poprawny / brak / błędny / unieważniony) |
| Typ testu | Funkcjonalny (bezpieczeństwo – uwierzytelnianie) |
| Poziom testu | Testowanie systemowe (REST API) |
| Warunki wstępne / dane | Użytkownik testowy; token `tok-<losowy>` z zakresem `read:user` |
| Powiązane funkcje | F12 |

| # | Krok | Oczekiwany rezultat |
|---|---|---|
| 1 | `POST /users/<user>/tokens` | 201, zwrócony `sha1` |
| 2 | `GET /user` z tokenem poprawnym | 200 |
| 3 | `GET /user` bez nagłówka `Authorization` | 401 |
| 4 | `GET /user` z tokenem `000…0` | 401 |
| 5 | Usuń token, `GET /user` z usuniętym tokenem | 401 |

Warunki końcowe: token usunięty.

---

## Przypadki niefunkcjonalne (ISO/IEC 25010:2023)

### TC-NF01 – Czas odpowiedzi pod obciążeniem
| Pole | Wartość |
|---|---|
| Priorytet | Wysoki |
| Charakterystyka | Wydajność (Performance efficiency) → zachowanie w czasie, wykorzystanie zasobów (przepustowość) |
| Technika | Testowanie obciążeniowe z profilem operacyjnym (mieszanka odczytów 3:3:2:2:1) |
| Typ testu | Niefunkcjonalny – wydajnościowy |
| Poziom testu | Testowanie systemowe |
| Warunki wstępne / dane | Repo `perf-target` z 20 zgłoszeniami; 20 wirtualnych użytkowników, narastanie 5/s, czas 30 s (CI: 15 s); narzędzie Locust 2.32 |
| Powiązane funkcje | F04, F05, F10 |

| # | Krok | Oczekiwany rezultat |
|---|---|---|
| 1 | Przygotuj dane testowe przez API | Repo i 20 zgłoszeń utworzone |
| 2 | Uruchom Locust w trybie headless z profilem `perf/locustfile.py` | Wygenerowany `reports/perf/locust_stats.csv` |
| 3 | Odczytaj statystyki zagregowane | Odsetek błędów = 0% |
| 4 | Odczytaj przepustowość | ≥ 10 żądań/s |
| 5 | Odczytaj 95. percentyl każdego typu żądania | p95 < 500 ms dla każdego |

Warunki końcowe: dane wydajnościowe zapisane w `reports/perf/summary.json`; repo usunięte.

### TC-NF02 – Czas ładowania kluczowych stron
| Pole | Wartość |
|---|---|
| Priorytet | Średni |
| Charakterystyka | Wydajność → zachowanie w czasie |
| Technika | Pomiar z użyciem Navigation Timing API (mediana z 3 próbek) |
| Typ testu | Niefunkcjonalny – wydajnościowy |
| Poziom testu | Testowanie systemowe (Selenium) |
| Warunki wstępne / dane | Zalogowany użytkownik, repo testowe; strony: `/`, `/explore/repos`, repo, lista zgłoszeń, `/user/settings` |
| Powiązane funkcje | F02, F04, F05, F10 |

| # | Krok | Oczekiwany rezultat |
|---|---|---|
| 1 | Zaloguj się w przeglądarce | Sesja aktywna |
| 2 | Dla każdej strony 3× otwórz i odczytaj `loadEventEnd - startTime` | Pomiar dostępny |
| 3 | Policz medianę dla każdej strony | Mediana < 2000 ms dla każdej strony |

Warunki końcowe: wyniki w `reports/page_load.json`.

### TC-NF03 – Zgodność kluczowych widoków z WCAG 2.1 AA
| Pole | Wartość |
|---|---|
| Priorytet | Średni |
| Charakterystyka | Zdolność do interakcji (Interaction capability) → inkluzywność / dostępność |
| Technika | Testowanie oparte na liście kontrolnej (reguły axe-core 4.10.2: wcag2a, wcag2aa, wcag21aa) |
| Typ testu | Niefunkcjonalny – dostępności |
| Poziom testu | Testowanie systemowe (Selenium + axe-core) |
| Warunki wstępne / dane | Widoki: logowanie, rejestracja, repo, lista zgłoszeń, nowe repo |
| Powiązane funkcje | F01, F02, F04, F05 |

| # | Krok | Oczekiwany rezultat |
|---|---|---|
| 1 | Otwórz widoki anonimowe i uruchom axe | Raport naruszeń dla każdego widoku |
| 2 | Zaloguj się, otwórz widoki wymagające sesji i uruchom axe | Raport naruszeń dla każdego widoku |
| 3 | Zapisz podsumowanie do `reports/axe.json` | Plik zawiera id, wpływ i liczbę węzłów |
| 4 | Sprawdź naruszenia o wpływie `critical` | Brak naruszeń krytycznych |

Warunki końcowe: raport dostępności zapisany. **Wynik: niezaliczony – DEF-02** (w automatyzacji oznaczony jako znany defekt, `xfail`).

### TC-NF04 – Podstawowe zabezpieczenia aplikacji webowej
| Pole | Wartość |
|---|---|
| Priorytet | Wysoki |
| Charakterystyka | Bezpieczeństwo (Security) → poufność, integralność |
| Technika | Testowanie oparte na liście kontrolnej (OWASP ASVS: V3 sesje, V4 kontrola dostępu, V14 nagłówki) |
| Typ testu | Niefunkcjonalny – bezpieczeństwa |
| Poziom testu | Testowanie systemowe (HTTP) |
| Warunki wstępne / dane | Użytkownik testowy; obca domena `http://evil.example` |
| Powiązane funkcje | F02, F07 |

| # | Krok | Oczekiwany rezultat |
|---|---|---|
| 1 | `GET /user/login`, sprawdź nagłówki | `X-Content-Type-Options: nosniff`, `X-Frame-Options: SAMEORIGIN` lub `DENY` |
| 2 | Zaloguj się, sprawdź `Set-Cookie` ciasteczka sesji | `HttpOnly` i `SameSite=Lax` |
| 3 | Jako zalogowany wyślij `POST /repo/create` z `Origin: evil.example`, `Sec-Fetch-Site: cross-site` | 403; repo nie powstało |
| 4 | Wyślij `POST /user/login` cross-site | 403 (**faktycznie 303 – DEF-01, oznaczony jako xfail**) |
| 5 | Anonimowo `GET` strony i surowego pliku repo prywatnego | 404 dla obu |

Warunki końcowe: brak utworzonych zasobów.

### TC-NF05 – Kompatybilność przeglądarek
| Pole | Wartość |
|---|---|
| Priorytet | Średni |
| Charakterystyka | Kompatybilność (Compatibility) → współistnienie / interoperacyjność; Elastyczność (Flexibility) → adaptowalność |
| Technika | Testowanie sparametryzowane (ten sam scenariusz w wielu konfiguracjach) |
| Typ testu | Niefunkcjonalny – kompatybilności |
| Poziom testu | Testowanie systemowe (Selenium) |
| Warunki wstępne / dane | Google Chrome 157, Microsoft Edge (lokalnie); w CI tylko Chrome |
| Powiązane funkcje | F02, F03 |

| # | Krok | Oczekiwany rezultat |
|---|---|---|
| 1 | Uruchom przeglądarkę i zaloguj się | Awatar w nawigacji |
| 2 | Utwórz repozytorium z README | Lista plików zawiera `README.md` |
| 3 | Wyloguj się | Link „Sign In” w nawigacji |

Warunki końcowe: identyczny wynik w każdej przeglądarce; repo usunięte.

---

## Macierz śledzenia (funkcje ↔ przypadki testowe)

| Przypadek | F01 | F02 | F03 | F04 | F05 | F06 | F07 | F08 | F09 | F10 | F11 | F12 | F13 | F14 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| TC-F01 | ● | | | | | | | | | | | | | |
| TC-F02 | ● | | | | | | | | | | | | | |
| TC-F03 | | ● | | | | | | | | | | | | |
| TC-F04 | | ● | | | | | | | | | | | | |
| TC-F05 | | | ● | ● | | | | | | | | | | |
| TC-F06 | | | ● | | | | | | | | | | | |
| TC-F07 | | | | | ● | | | | ● | | | | | |
| TC-F08 | | | | | ● | | | | | | | | | |
| TC-F09 | | | | ● | | | | ● | | | | | | |
| TC-F10 | | | | | | ● | | | | | | | | |
| TC-F11 | | | | | | | | | | ● | | | | |
| TC-F12 | | ● | | | | | ● | | | | | | | |
| TC-F13 | | | ● | | | | | | | | | | | |
| TC-F14 | | | | | | | ● | | | | | | | |
| TC-F15 | | | | | | | ● | | | | | | | |
| TC-F16 | | | | | ● | | | | ● | | | | | |
| TC-F17 | | | | | | | | | | | | ● | | |
| TC-NF01 | | | | ● | ● | | | | | ● | | | | |
| TC-NF02 | | ● | | ● | ● | | | | | ● | | | | |
| TC-NF03 | ● | ● | | ● | ● | | | | | | | | | |
| TC-NF04 | | ● | | | | | ● | | | | | | | |
| TC-NF05 | | ● | ● | | | | | | | | | | | |
| **Liczba TC** | 3 | 7 | 4 | 5 | 6 | 1 | 4 | 1 | 2 | 3 | 0 | 1 | 0 | 0 |

Priorytety MoSCoW funkcji: F01–F07 Must, F08–F10 Should, F11–F13 Could, F14 Won't.
Pokrycie funkcji: 11/14 (79%); Must 7/7 (100%), Should 3/3 (100%), Could 1/3, Won't 0/1 (poza zakresem).

## Podsumowanie przypadków

| ID | Tytuł | Priorytet | Technika | Poziom | Funkcje | Automatyzacja | Wynik |
|---|---|---|---|---|---|---|---|
| TC-F01 | Rejestracja poprawnymi danymi | Wysoki | Klasy równoważności | Systemowy / UI | F01 | Selenium | Zaliczony |
| TC-F02 | Minimalna długość hasła | Wysoki | Wartości brzegowe | Systemowy / UI | F01 | Selenium | Zaliczony |
| TC-F03 | Logowanie poprawne | Wysoki | Klasy równoważności | Systemowy / UI | F02 | Selenium | Zaliczony |
| TC-F04 | Logowanie z błędnym hasłem | Wysoki | Klasy równoważności | Systemowy / UI | F02 | Selenium | Zaliczony |
| TC-F05 | Repozytorium z README | Wysoki | Klasy równoważności | Systemowy / UI | F03, F04 | Selenium | Zaliczony |
| TC-F06 | Duplikat nazwy repo | Średni | Zgadywanie błędów | Systemowy / UI | F03 | Selenium | Zaliczony |
| TC-F07 | Zgłoszenie z etykietą | Wysoki | Kryteria akceptacji | Systemowy / UI | F05, F09 | Selenium | Zaliczony |
| TC-F08 | Zamknięcie i ponowne otwarcie zgłoszenia | Wysoki | Przejścia między stanami | Systemowy / UI | F05 | Selenium | Zaliczony |
| TC-F09 | Edycja pliku w edytorze | Średni | Kryteria akceptacji | Systemowy / UI | F08, F04 | Selenium | Zaliczony |
| TC-F10 | Pull request i merge | Wysoki | Kryteria akceptacji | Systemowy / UI | F06 | Selenium | Zaliczony |
| TC-F11 | Wyszukiwanie repozytorium | Średni | Klasy równoważności | Systemowy / UI | F10 | Selenium | Zaliczony |
| TC-F12 | Wylogowanie a dostęp do ustawień | Wysoki | Przejścia między stanami | Systemowy / UI | F02, F07 | Selenium | Zaliczony |
| TC-F13 | CRUD repozytorium | Wysoki | Kryteria akceptacji | Systemowy / API | F03 | requests | Zaliczony |
| TC-F14 | Widoczność repo wg roli | Wysoki | Tablica decyzyjna | Systemowy / API | F07 | requests | Zaliczony |
| TC-F15 | Kolaborator | Wysoki | Przejścia między stanami | Systemowy / API | F07 | requests | Zaliczony |
| TC-F16 | Postęp milestone | Średni | Kryteria akceptacji | Systemowy / API | F09, F05 | requests | Zaliczony |
| TC-F17 | Token API | Średni | Klasy równoważności | Systemowy / API | F12 | requests | Zaliczony |
| TC-NF01 | Czas odpowiedzi pod obciążeniem | Wysoki | Test obciążeniowy | Systemowy | F04, F05, F10 | Locust | Zaliczony |
| TC-NF02 | Czas ładowania stron | Średni | Pomiar Navigation Timing | Systemowy / UI | F02, F04, F05, F10 | Selenium | Zaliczony |
| TC-NF03 | WCAG 2.1 AA | Średni | Lista kontrolna (axe) | Systemowy / UI | F01, F02, F04, F05 | Selenium + axe | **Niezaliczony (DEF-02, xfail)** |
| TC-NF04 | Zabezpieczenia aplikacji | Wysoki | Lista kontrolna (ASVS) | Systemowy | F02, F07 | requests | Zaliczony (DEF-01 xfail) |
| TC-NF05 | Kompatybilność przeglądarek | Średni | Test sparametryzowany | Systemowy / UI | F02, F03 | Selenium | Zaliczony |
