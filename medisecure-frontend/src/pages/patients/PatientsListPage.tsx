// src/pages/patients/PatientsListPage.tsx
import React, { useEffect, useState, useCallback } from "react";
import { Link, useLocation } from "react-router-dom";
import { Patient } from "../../types/patient.types";
import patientService from "../../api/services/patientService";
import toast from "react-hot-toast";
import Button from "../../components/common/Button/Button";
import Alert from "../../components/common/Alert/Alert";
import LoadingScreen from "../../components/common/LoadingScreen/LoadingScreen";

const PatientsListPage: React.FC = () => {
  const [patients, setPatients] = useState<Patient[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [filteredPatients, setFilteredPatients] = useState<Patient[]>([]);
  const location = useLocation();

  // Utiliser useCallback pour éviter les récursions infinies dans useEffect
  const fetchPatients = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      // Appel réel à l'API
      const fetchedPatients = await patientService.getAllPatients();
      console.log("Patients récupérés:", fetchedPatients);
      setPatients(fetchedPatients);
      // Réinitialiser les patients filtrés quand on recharge la liste complète
      setFilteredPatients(fetchedPatients);
    } catch (error) {
      console.error("Erreur lors du chargement des patients:", error);
      setError("Impossible de charger la liste des patients");
    } finally {
      setLoading(false);
    }
  }, []);

  // Recharger les données quand la page change ou quand l'URL change
  useEffect(() => {
    fetchPatients();
  }, [fetchPatients, location.key]); // location.key change quand on navigue

  // Filtrer les patients en fonction de la recherche
  useEffect(() => {
    if (!searchQuery.trim()) {
      setFilteredPatients(patients);
      return;
    }

    const query = searchQuery.toLowerCase().trim();
    const filtered = patients.filter(
      (patient) =>
        patient.firstName.toLowerCase().includes(query) ||
        patient.lastName.toLowerCase().includes(query) ||
        patient.email?.toLowerCase().includes(query) ||
        patient.phone?.includes(query)
    );

    setFilteredPatients(filtered);
  }, [searchQuery, patients]);

  // Calculer l'âge à partir de la date de naissance
  const calculateAge = (dateOfBirth: string): number => {
    const today = new Date();
    const birthDate = new Date(dateOfBirth);
    let age = today.getFullYear() - birthDate.getFullYear();
    const monthDiff = today.getMonth() - birthDate.getMonth();

    if (
      monthDiff < 0 ||
      (monthDiff === 0 && today.getDate() < birthDate.getDate())
    ) {
      age--;
    }

    return age;
  };

  // Gérer la suppression d'un patient
  const handleDeletePatient = async (id: string) => {
    if (!window.confirm("Êtes-vous sûr de vouloir supprimer ce patient ?")) {
      return;
    }

    try {
      await patientService.deletePatient(id);
      // Mettre à jour l'état local immédiatement après succès
      setPatients((prevPatients) =>
        prevPatients.filter((patient) => patient.id !== id)
      );
      setFilteredPatients((prevPatients) =>
        prevPatients.filter((patient) => patient.id !== id)
      );
      toast.success("Patient supprimé avec succès");
    } catch (error) {
      console.error("Erreur lors de la suppression du patient:", error);
      toast.error("Erreur lors de la suppression du patient");
    }
  };

  if (loading) {
    return <LoadingScreen />;
  }

  return (
    <div className="space-y-6">
      {/* En-tête */}
      <div className="flex flex-col md:flex-row md:justify-between md:items-center space-y-4 md:space-y-0">
        <h1 className="text-2xl font-semibold text-slate-900">Patients</h1>
        <Link
          to="/patients/create"
          className="btn btn-primary inline-flex items-center"
        >
          <svg
            className="h-5 w-5 mr-2"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 6v6m0 0v6m0-6h6m-6 0H6"
            />
          </svg>
          Nouveau patient
        </Link>
      </div>

      {error && (
        <Alert variant="error" message={error} onClose={() => setError(null)} />
      )}

      {/* Barre de recherche */}
      <div className="relative">
        <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
          <svg
            className="h-5 w-5 text-slate-400"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
            />
          </svg>
        </div>
        <input
          type="text"
          className="input pl-10"
          placeholder="Rechercher un patient..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
        />
      </div>

      {/* Liste des patients */}
      <div className="card overflow-hidden">
        <div className="overflow-x-auto -mx-6 px-6">
          <table className="min-w-full divide-y divide-neutral-200">
            <thead>
              <tr>
                <th className="px-3 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">
                  Nom
                </th>
                <th className="px-3 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">
                  Informations
                </th>
                <th className="px-3 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">
                  Contact
                </th>
                <th className="px-3 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">
                  Numéro d'assurance
                </th>
                <th className="px-3 py-3 text-right text-xs font-medium text-slate-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-neutral-200">
              {filteredPatients.length === 0 ? (
                <tr>
                  <td
                    colSpan={5}
                    className="px-3 py-4 text-center text-slate-500"
                  >
                    Aucun patient trouvé
                  </td>
                </tr>
              ) : (
                filteredPatients.map((patient) => (
                  <tr key={patient.id} className="hover:bg-slate-50">
                    <td className="px-3 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <div className="h-10 w-10 rounded-full bg-primary-100 flex items-center justify-center text-primary-700">
                          {patient.firstName.charAt(0) +
                            patient.lastName.charAt(0)}
                        </div>
                        <div className="ml-3">
                          <div className="text-sm font-medium text-slate-900">
                            {patient.firstName} {patient.lastName}
                          </div>
                          <div className="text-xs text-slate-500">
                            ID: {patient.id}
                          </div>
                        </div>
                      </div>
                    </td>
                    <td className="px-3 py-4 whitespace-nowrap">
                      <div className="text-sm text-slate-900">
                        {new Date(patient.dateOfBirth).toLocaleDateString(
                          "fr-FR"
                        )}
                      </div>
                      <div className="text-xs text-slate-500">
                        {calculateAge(patient.dateOfBirth)} ans -{" "}
                        {patient.gender === "male" ? "Homme" : "Femme"}
                      </div>
                    </td>
                    <td className="px-3 py-4 whitespace-nowrap">
                      <div className="text-sm text-slate-900">
                        {patient.email || "Non renseigné"}
                      </div>
                      <div className="text-xs text-slate-500">
                        {patient.phone || "Non renseigné"}
                      </div>
                    </td>
                    <td className="px-3 py-4 whitespace-nowrap">
                      <div className="text-sm text-slate-900">
                        {patient.insuranceNumber || "Non renseigné"}
                      </div>
                    </td>
                    <td className="px-3 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <Link
                        to={`/patients/${patient.id.replace(/\s+/g, "-")}`}
                        className="text-primary-600 hover:text-primary-900 mr-3"
                      >
                        Détails
                      </Link>
                      <Link
                        to={`/patients/${patient.id.replace(/\s+/g, "-")}/edit`}
                        className="text-secondary-600 hover:text-secondary-900 mr-3"
                      >
                        Modifier
                      </Link>
                      <button
                        onClick={() => handleDeletePatient(patient.id)}
                        className="text-error-500 hover:text-error-700"
                      >
                        Supprimer
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Bouton pour rafraîchir les données */}
      <div className="flex justify-center">
        <Button variant="outline" onClick={fetchPatients} isLoading={loading}>
          Rafraîchir la liste
        </Button>
      </div>
    </div>
  );
};

export default PatientsListPage;
