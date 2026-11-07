# Analiza produktu – funkcje Gitea 28.3.0 i priorytety MoSCoW

Priorytet określa ważność funkcji dla użytkownika i wynikające z niej ryzyko produktowe,
które wyznacza intensywność testowania (testowanie oparte na ryzyku).

| ID | Funkcja | Opis | MoSCoW | Uzasadnienie |
|---|---|---|---|---|
| F01 | Rejestracja konta | Założenie konta przez formularz `/user/sign_up` z walidacją nazwy, e-maila i hasła (min. 8 znaków). | Must | Wejście każdego nowego użytkownika do systemu. |
| F02 | Logowanie i wylogowanie | Uwierzytelnienie nazwą/e-mailem i hasłem, sesja w ciasteczku, wylogowanie z menu użytkownika. | Must | Warunek wstępny niemal wszystkich pozostałych funkcji. |
| F03 | Zarządzanie repozytoriami | Tworzenie (publiczne/prywatne, inicjalizacja README), edycja ustawień i usuwanie repozytoriów. | Must | Podstawowy obiekt domeny aplikacji. |
| F04 | Przeglądanie kodu i historii | Lista plików, podgląd README, historia commitów, gałęzie. | Must | Główny sposób korzystania z repozytorium. |
| F05 | Zgłoszenia (issues) | Tworzenie, komentowanie, zamykanie i ponowne otwieranie zgłoszeń. | Must | Kluczowy proces śledzenia błędów i zadań. |
| F06 | Pull requesty | Porównanie gałęzi, utworzenie PR, przegląd zmian, merge. | Must | Rdzeń współpracy nad kodem. |
| F07 | Kontrola dostępu | Widoczność repo prywatnych, kolaboratorzy z uprawnieniami, ochrona zasobów przed anonimami. | Must | Poufność danych – naruszenie ma wysoki wpływ. |
| F08 | Edytor plików w przeglądarce | Edycja pliku w UI i commit bezpośrednio do gałęzi lub nowej gałęzi. | Should | Wygodne, ale istnieje alternatywa (klient git). |
| F09 | Etykiety i kamienie milowe | Kategoryzacja zgłoszeń etykietami, grupowanie w milestone z licznikiem postępu. | Should | Organizacja pracy zespołu. |
| F10 | Wyszukiwanie | Wyszukiwanie repozytoriów, użytkowników i zgłoszeń (Explore). | Should | Istotne przy dużej liczbie repozytoriów. |
| F11 | Organizacje i zespoły | Grupowanie repo w organizacjach, zespoły z uprawnieniami. | Could | Potrzebne większym zespołom; poza krytyczną ścieżką. |
| F12 | Profil i tokeny API | Ustawienia konta, tokeny dostępu do REST API z zakresami (scopes). | Could | Wykorzystywane przez integracje i automatyzację. |
| F13 | Wiki repozytorium | Strony dokumentacji przy repozytorium. | Could | Funkcja dodatkowa. |
| F14 | Gitea Actions (CI) | Wbudowany system CI kompatybilny z GitHub Actions. | Won't | Poza zakresem – wymaga runnerów, osobny przedmiot testów. |

Podsumowanie: 7 × Must, 3 × Should, 3 × Could, 1 × Won't.
Funkcje Must są pokryte przypadkami funkcjonalnymi na poziomie UI i/lub API oraz testami
niefunkcjonalnymi; F11 i F13 świadomie nie są pokryte (ryzyko rezydualne, zob. raport §8).
