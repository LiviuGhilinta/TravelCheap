Proiectul „ Travel Cheap” este o aplicatie desktop care ajuta utilizatorul sa caute si sa compare cele mai ieftine bilete si sa obtina prognoza meteo pentru perioada si destinatia aleasa.
Limbaj de programare utilizat: Python3.13.
Module utilizate: sys, PyQT5, json, requests, datetime. Dintre care PyQT5, requests trebuiesc instalate cu comanda pip din terminal.
Editor: Visual Studio Code
Cautarea datelor despre bilete si vreme sunt facute prin apelarea API -urilor: SerpAPI si VisualCrossingWeb. 
Utilizare:
1.	Deschide fisierul "Airport_Search.py" si da RUN
2.	Apasa Butonul "Let’s start"
3.	Selecteaza tipul de zbor (dus / dus-intors)
4.	Selecteaza perioada dorita de calatorie folosind calendarul
5.	Apasa pe butonul de "Search" pentru a obtine rezultatele
6.	In urmatoarea pagina vei gasi cele mai ieftine bilete de la companiile low-cost, cu link direct catre pagina de cumparare a biletelor si detalii despre pretul biletelor si zbor
7.	In partea de jos, este prezenta prognoza meteo pentru primele 3 zile din perioada selectata
8.	Pentru a inchide aplicatia, foloseste butonul X prezent pe fiecare pagina