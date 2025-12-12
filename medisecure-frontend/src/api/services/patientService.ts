// src/api/services/patientService.ts
import apiClient from "../apiClient";
import { ENDPOINTS } from "../endpoints";
import {
  Patient,
  PatientCreateDto,
  PatientUpdateDto,
} from "../../types/patient.types";

// Interface pour adapter les réponses de l'API
interface PatientListResponse {
  patients: any[];
  total: number;
  skip: number;
  limit: number;
}

// Fonction pour adapter les DTO du front vers le back
const adaptPatientCreateDto = (frontDto: PatientCreateDto): any => {
  return {
    first_name: frontDto.firstName,
    last_name: frontDto.lastName,
    date_of_birth: frontDto.dateOfBirth,
    gender: frontDto.gender,
    email: frontDto.email || null,
    phone_number: frontDto.phone || null,
    address: frontDto.address || null,
    insurance_id: frontDto.insuranceNumber || null,
    notes: frontDto.medicalHistory || null,

    // Ajout des champs obligatoires manquants
    city: null,
    postal_code: null,
    country: null,
    blood_type: null,
    allergies: {},
    chronic_diseases: {},
    current_medications: {},
    has_consent: true,
    gdpr_consent: true,
    has_guardian_consent: false,
    insurance_provider: null,
  };
};

// Fonction pour adapter les DTO du back vers le front
const adaptPatientFromApi = (backDto: any): Patient => {
  return {
    id: backDto.id,
    firstName: backDto.first_name,
    lastName: backDto.last_name,
    dateOfBirth: backDto.date_of_birth,
    gender: backDto.gender as "male" | "female" | "other",
    email: backDto.email,
    phone: backDto.phone_number,
    address: backDto.address,
    insuranceNumber: backDto.insurance_id,
    medicalHistory: backDto.notes,
    createdAt: backDto.created_at,
    updatedAt: backDto.updated_at,
  };
};

// Fonction pour adapter les DTO de mise à jour
const adaptPatientUpdateDto = (frontDto: PatientUpdateDto): any => {
  const backDto: any = {};

  if (frontDto.firstName !== undefined) backDto.first_name = frontDto.firstName;
  if (frontDto.lastName !== undefined) backDto.last_name = frontDto.lastName;
  if (frontDto.dateOfBirth !== undefined)
    backDto.date_of_birth = frontDto.dateOfBirth;
  if (frontDto.gender !== undefined) backDto.gender = frontDto.gender;
  if (frontDto.email !== undefined) backDto.email = frontDto.email;
  if (frontDto.phone !== undefined) backDto.phone_number = frontDto.phone;
  if (frontDto.address !== undefined) backDto.address = frontDto.address;
  if (frontDto.insuranceNumber !== undefined)
    backDto.insurance_id = frontDto.insuranceNumber;
  if (frontDto.medicalHistory !== undefined)
    backDto.notes = frontDto.medicalHistory;

  return backDto;
};

const patientService = {
  getAllPatients: async (): Promise<Patient[]> => {
    try {
      const response = await apiClient.get<PatientListResponse>(
        ENDPOINTS.PATIENTS.BASE
      );
      return response.patients.map(adaptPatientFromApi);
    } catch (error) {
      console.error("Erreur lors de la récupération des patients:", error);
      throw error;
    }
  },

  getPatientById: async (id: string): Promise<Patient> => {
    try {
      const cleanId = id.replace(/\s+/g, "-");
      const response = await apiClient.get<any>(ENDPOINTS.PATIENTS.DETAIL(cleanId));
      return adaptPatientFromApi(response);
    } catch (error) {
      console.error(`Erreur lors de la récupération du patient ${id}:`, error);
      throw error;
    }
  },

  createPatient: async (patient: PatientCreateDto): Promise<Patient> => {
    try {
      const adaptedPatient = adaptPatientCreateDto(patient);
      console.log("Envoi des données au backend:", adaptedPatient);
      const response = await apiClient.post<any>(
        ENDPOINTS.PATIENTS.BASE,
        adaptedPatient
      );
      console.log("Réponse du backend après création:", response);
      return adaptPatientFromApi(response);
    } catch (error) {
      console.error("Erreur lors de la création du patient:", error);
      throw error;
    }
  },

  updatePatient: async (
    id: string,
    patient: PatientUpdateDto
  ): Promise<Patient> => {
    try {
      const adaptedPatient = adaptPatientUpdateDto(patient);
      console.log(`Mise à jour du patient ${id}:`, adaptedPatient);
      const response = await apiClient.put<any>(
        ENDPOINTS.PATIENTS.DETAIL(id),
        adaptedPatient
      );
      console.log("Réponse du backend après mise à jour:", response);
      return adaptPatientFromApi(response);
    } catch (error) {
      console.error(`Erreur lors de la mise à jour du patient ${id}:`, error);
      throw error;
    }
  },

  deletePatient: async (id: string): Promise<void> => {
    try {
      console.log(`Suppression du patient ${id}`);
      await apiClient.delete(ENDPOINTS.PATIENTS.DETAIL(id));
      console.log(`Patient ${id} supprimé avec succès`);
    } catch (error) {
      console.error(`Erreur lors de la suppression du patient ${id}:`, error);
      throw error;
    }
  },

  searchPatients: async (query: string): Promise<Patient[]> => {
    try {
      const response = await apiClient.post<PatientListResponse>(
        ENDPOINTS.PATIENTS.SEARCH,
        { name: query, skip: 0, limit: 100 }
      );
      return response.patients.map(adaptPatientFromApi);
    } catch (error) {
      console.error("Erreur lors de la recherche de patients:", error);
      throw error;
    }
  },
};

export default patientService;
