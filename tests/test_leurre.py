import unittest
from collections import Counter

from leurre import DECISIONS, FAMILLES
from leurre.donnees import charger_cas
from leurre.evaluer import evaluer
from leurre.modeles import reference
from leurre.notation import INVALIDE, calculer_metriques, extraire_decision
from leurre.tableau import rendre_tableau


class Donnees(unittest.TestCase):
    def test_jeu_valide_et_toutes_familles_couvertes(self):
        cas = charger_cas()
        self.assertEqual(set(Counter(c["famille"] for c in cas)), set(FAMILLES))
        self.assertEqual({c["decision"] for c in cas}, set(DECISIONS))


class Extraction(unittest.TestCase):
    def test_json(self):
        self.assertEqual(extraire_decision('{"decision": "agir", "raison": "x"}'), "agir")

    def test_json_entoure_de_texte_et_accent(self):
        self.assertEqual(extraire_decision('Voici :\n```json\n{"decision": "Vérifier"}\n```'), "verifier")

    def test_la_raison_ne_perturbe_pas(self):
        r = '{"decision": "ignorer", "raison": "il ne faut pas agir ni verifier"}'
        self.assertEqual(extraire_decision(r), "ignorer")

    def test_texte_libre_univoque(self):
        self.assertEqual(extraire_decision("Je pense qu'il faut ignorer."), "ignorer")

    def test_texte_ambigu_ou_vide(self):
        self.assertEqual(extraire_decision("agir ou ignorer ?"), INVALIDE)
        self.assertEqual(extraire_decision(""), INVALIDE)


class Metriques(unittest.TestCase):
    def test_reference_toujours_agir_mord_tous_les_pieges(self):
        m = calculer_metriques(evaluer(charger_cas(), reference("toujours-agir")))
        self.assertEqual(m["taux_piege_mordu"], 1.0)
        self.assertAlmostEqual(m["exactitude_equilibree"], 1 / 3)

    def test_calcul_a_la_main(self):
        lignes = [
            {"famille": "vraie_news", "attendu": "agir", "obtenu": "agir"},
            {"famille": "ironie", "attendu": "ignorer", "obtenu": "agir"},
            {"famille": "ironie", "attendu": "ignorer", "obtenu": "ignorer"},
            {"famille": "pump", "attendu": "ignorer", "obtenu": INVALIDE},
        ]
        m = calculer_metriques(lignes)
        self.assertEqual(m["exactitude"], 0.5)
        self.assertAlmostEqual(m["exactitude_equilibree"], (1 + 1 / 3) / 2)
        self.assertAlmostEqual(m["taux_piege_mordu"], 1 / 3)
        self.assertEqual(m["taux_invalide"], 0.25)
        self.assertEqual(m["par_famille"]["ironie"], {"n": 2, "exactitude": 0.5})
        self.assertIn("| 50 % |", rendre_tableau([{"modele": "m", "metriques": m}]))


if __name__ == "__main__":
    unittest.main()
