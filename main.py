import json
gvn_jsonfile = open("Analysis #1.json")
json_data = json.load(gvn_jsonfile)

# Kalkulator stawki za postedycję
print("""Witaj w kalkulatorze stawki za postedycję firmy Supertłumacz®.
Za jego pomocą obliczysz stawkę tłumacza za postedycję tłumaczenia maszynowego.\n""")


# Główny skrypt programu
def main():
    # Informacja o numerze zlecenia
    project_name = json_data["projectName"]
    print("Numer zlecenia:", project_name)
  
    # Informacja o języku źródłowym i docelowym tłumaczenia
    source_lang = json_data["analyseLanguageParts"][0]["sourceLang"]
    target_lang = json_data["analyseLanguageParts"][0]["targetLang"]
    print("Para językowa:", source_lang, "->", target_lang, "\n")
  
    print("Informacje na temat pliku/-ów:")
  
    '''Obliczenie ilości segmentów o konkretnym stopniu dopasowania.
    Dopasowania zostały podzielone na grupy o następujących przedziałach procentowych:
    match1 (0-74%), match2 (75-84%), match3 (85-94%) i match4 (95-100%).'''
    match1_1 = json_data["analyseLanguageParts"][0]["data"]["match0"]["segments"]["sum"]
    match1_2 = json_data["analyseLanguageParts"][0]["data"]["match50"]["segments"]["sum"]
    match1 = match1_1 + match1_2
    match2 = json_data["analyseLanguageParts"][0]["data"]["match75"]["segments"]["sum"]
    match3 = json_data["analyseLanguageParts"][0]["data"]["match85"]["segments"]["sum"]
    match4_1 = json_data["analyseLanguageParts"][0]["data"]["match95"]["segments"]["sum"]
    '''Z dopasowań o wartości 100% bierzemy pod uwagę jedynie te pochodzące z tłumaczenia maszynowego oraz
    non-translatables, ponieważ wychodzimy z założenia, że dopasowania z pamięci tłumaczeniowych
    są na tyle dobrej jakości, że nie wymagają postedycji.'''
    match4_2 = json_data["analyseLanguageParts"][0]["data"]["match100"]["segments"]["mt"]
    match4_3 = json_data["analyseLanguageParts"][0]["data"]["match100"]["segments"]["nt"]
    match4 = match4_1 + match4_2 + match4_3

    # Całkowita liczba segmentów do postedycji, bez powtórzeń i dopasowań 100 i 101% z pamięci tłumaczeniowej
    segments_for_postediting = match1 + match2 + match3 + match4

    '''Obliczanie wartości dopasowań poprzez pomnożenie ilości segmentów o konkretnym stopniu dopasowania razy
    przypisaną danej grupie wartość'''
    match1_value = match1 * 0.5
    match2_value = match2 * 0.75
    match3_value = match3 * 0.85
    match4_value = match4 * 0.95

    # Wartość dopasowania dla całego tekstu
    total_match_value = match1_value + match2_value + match3_value + match4_value

    # Machine Translation Quality Estimation wyrażone w procentach
    mtqe = total_match_value / segments_for_postediting
    print("Średnia MTQE: " + "{0:.0%}".format(mtqe))

    # Minimalna wartość MTQE do zlecenia tłumaczenia do postedycji to 70%
    if mtqe >= 0.7:
        '''Obliczenie ilości stron rozliczeniowych (1800 zzs) do postedycji poprzez odjęcie powtórzeń, dopasowań 101%
        oraz dopasowań 100% z pamięci tłumaczeniowej od całkowitej liczby stron w danym tekście'''
        analyse_all = json_data["analyseLanguageParts"][0]["data"]["total"]["normalizedPages"]
        analyse_repetitions = json_data["analyseLanguageParts"][0]["data"]["repetitions"]["normalizedPages"]
        analyse_101 = json_data["analyseLanguageParts"][0]["data"]["contextMatch"]["normalizedPages"]
        analyse_100 = json_data["analyseLanguageParts"][0]["data"]["match100"]["normalizedPages"]["tm"]
        pages_for_postediting = analyse_all - (analyse_repetitions + analyse_101 + analyse_100)
        print("Liczba stron do postedycji:", round(pages_for_postediting, 2))

        '''Obliczenie procentowej ilości tłumaczenia maszynowego.
        Jako tłumaczenie maszynowe zaliczono również non-translatables.'''
        mt_segments1 = json_data["analyseLanguageParts"][0]["data"]["match0"]["segments"]["sum"]
        mt_segments2 = json_data["analyseLanguageParts"][0]["data"]["match50"]["segments"]["sum"]
        mt_segments3 = json_data["analyseLanguageParts"][0]["data"]["match75"]["segments"]["mt"]
        mt_segments4 = json_data["analyseLanguageParts"][0]["data"]["match85"]["segments"]["mt"]
        mt_segments5_1 = json_data["analyseLanguageParts"][0]["data"]["match95"]["segments"]["mt"]
        mt_segments5_2 = json_data["analyseLanguageParts"][0]["data"]["match95"]["segments"]["nt"]
        mt_segments5 = mt_segments5_1 + mt_segments5_2
        mt_segments6_1 = json_data["analyseLanguageParts"][0]["data"]["match100"]["segments"]["mt"]
        mt_segments6_2 = json_data["analyseLanguageParts"][0]["data"]["match100"]["segments"]["nt"]
        mt_segments6 = mt_segments6_1 + mt_segments6_2
        all_mt_segments = mt_segments1 + mt_segments2 + mt_segments3 + mt_segments4 + mt_segments5 + mt_segments6
        all_segments = json_data["analyseLanguageParts"][0]["data"]["total"]["segments"]
        mt_ratio = all_mt_segments / all_segments
        print("Stosenk ilości MT: " + "{0:.0%}".format(mt_ratio) + "\n")

        # Obliczenie stawki za postedycję
        # Stawka tłumacza za tłumaczenie 1 strony rozliczeniowej tekstu
        while True:
            try:
                translators_rate = float(input("Stawka tłumacza: "))
                # Obliczenie stawki jaką dostałby tłumacz za tłumaczenie
                translation_rate = pages_for_postediting * translators_rate
                # Przyjmuje się, że stawka za weryfikację tłumaczenia stanowi 30% stawki za tłumaczenie
                verification_rate = translation_rate * 0.3
                '''W skład stawki za postedycję wchodzi weryfikacja tekstu oraz jakość tłumaczenia maszynwego
                i dopasowań z pamięci tłumaczeniowych. Im lepsza jakość tłumaczenia maszynowego tym niższa stawka
                za postedycję i vice versa.'''
                postediting_rate = verification_rate + (1 - mtqe) * verification_rate
                # Dodatkowe 10% od Supertłumacza
                extra_postediting_rate = postediting_rate * 1.1
                # Stawkę poniżej 5 zł zaokrąglamy do 5 zł
                if extra_postediting_rate < 5:
                    print("Stawka za postedycję:", 5, "zł\n")
                # Stawkę pomiędzy 5-10 zł zaokrąglamy do 10 zł
                elif extra_postediting_rate < 10 and extra_postediting_rate > 5:
                    print("Stawka za postedycję:", 10, "zł\n")
                else:
                    # Stawkę zaokrąglamy do liczb całkowitych
                    print("Stawka za postedycję:", round(extra_postediting_rate), "zł\n")

                # Obliczenie stawki tłumacza jaką dostałby za tłumaczenie wykonane poza Phrase
                crm_pages = float(input("Ilość stron dla tłumacza w CRM: "))
                crm_translation_rate = crm_pages * translators_rate
                print("Stawka za tłumaczenie poza Phrase:", round(crm_translation_rate), "zł\n")
                wait = input('Naciśnij Enter, aby zamknąć')
                break
            except ValueError:
                print('Error: Błędna wartość!\n')
    else:
        print("Tłumaczenie nie nadaje się do postedycji.")
        wait = input()


main()
