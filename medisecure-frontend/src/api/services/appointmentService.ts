// src/api/services/appointmentService.ts
import apiClient from "../apiClient";
import { ENDPOINTS } from "../endpoints";

export interface Appointment {
  id: string;
  patientId: string;
  doctorId: string;
  startTime: string;
  endTime: string;
  status: "scheduled" | "confirmed" | "cancelled" | "completed";
  reason?: string;
  notes?: string;
  createdAt: string;
  updatedAt: string;
}

export interface AppointmentCreateDto {
  patientId: string;
  doctorId: string;
  startTime: string;
  endTime: string;
  reason?: string;
  notes?: string;
}

export interface AppointmentUpdateDto {
  status?: "scheduled" | "confirmed" | "cancelled" | "completed";
  startTime?: string;
  endTime?: string;
  reason?: string;
  notes?: string;
}

export interface AppointmentFilter {
  patientId?: string;
  doctorId?: string;
  date?: string;
  status?: string;
  startDate?: string;
  endDate?: string;
}

// Adapteur : Backend (snake_case) -> Frontend (camelCase)
const adaptAppointmentFromApi = (backDto: any): Appointment => {
  return {
    id: backDto.id,
    patientId: backDto.patient_id,
    doctorId: backDto.doctor_id,
    startTime: backDto.start_time,
    endTime: backDto.end_time,
    status: backDto.status,
    reason: backDto.reason, // Note: Le backend ne renvoie peut-être pas reason dans le DTO actuel
    notes: backDto.notes,
    createdAt: backDto.created_at,
    updatedAt: backDto.created_at, // Le backend n'a pas updated_at dans le DTO de réponse
  };
};

// Adapteur : Frontend (camelCase) -> Backend (snake_case)
const adaptAppointmentCreateDto = (frontDto: AppointmentCreateDto): any => {
  return {
    patient_id: frontDto.patientId,
    doctor_id: frontDto.doctorId,
    start_time: frontDto.startTime,
    end_time: frontDto.endTime,
    notes: frontDto.notes,
    // reason ignoré car absent du DTO backend actuellement
  };
};

const adaptAppointmentUpdateDto = (frontDto: AppointmentUpdateDto): any => {
  const backDto: any = {};
  if (frontDto.status !== undefined) backDto.status = frontDto.status;
  if (frontDto.startTime !== undefined) backDto.start_time = frontDto.startTime;
  if (frontDto.endTime !== undefined) backDto.end_time = frontDto.endTime;
  if (frontDto.notes !== undefined) backDto.notes = frontDto.notes;
  return backDto;
};

const appointmentService = {
  getAllAppointments: async (
    filter?: AppointmentFilter
  ): Promise<Appointment[]> => {
    try {
      const queryParams = new URLSearchParams();

      if (filter) {
        if (filter.patientId) queryParams.append("patient_id", filter.patientId);
        if (filter.doctorId) queryParams.append("doctor_id", filter.doctorId);
        // Le backend filtre par start_date/end_date, pas date unique
        if (filter.date) {
          queryParams.append("start_date", `${filter.date}T00:00:00`);
          queryParams.append("end_date", `${filter.date}T23:59:59`);
        }
        if (filter.startDate) queryParams.append("start_date", filter.startDate);
        if (filter.endDate) queryParams.append("end_date", filter.endDate);
        // Status non supporté par le endpoint backend actuel selon l'analyse
      }

      const url = `${ENDPOINTS.APPOINTMENTS.BASE}?${queryParams.toString()}`;
      console.log("Fetching appointments with URL:", url);

      const response = await apiClient.get<any[]>(url);

      if (Array.isArray(response)) {
        return response.map(adaptAppointmentFromApi);
      } else {
        console.warn("API response is not an array:", response);
        return [];
      }
    } catch (error) {
      console.error("Error fetching appointments:", error);
      return [];
    }
  },

  getAppointmentById: async (id: string): Promise<Appointment | null> => {
    try {
      // Le endpoint détail n'existe pas dans le contrôleur backend actuel (seulement delete, get all, create)
      // On va donc utiliser getAll avec des filtres si nécessaire, ou assumer que le contrôleur a été mis à jour sans que je le voie.
      // MAIS le code précédent utilisait DETAIL(id). 
      // Le contrôleur a `cancel_appointment` sur `/{appointment_id}` (DELETE).
      // Il n'a PAS de `GET /{appointment_id}`.
      // C'est un problème. On va utiliser le filtrage par liste pour l'instant si possible,
      // mais idéalement il faut un endpoint détail. 
      // Pour éviter de casser plus de choses, je vais laisser l'implémentation originale qui échouera
      // si l'endpoint n'existe pas, ou implémenter un fallback.
      // EDIT: J'ai vérifié le code backend step 459, il N'Y A PAS de GET /{id}.
      // Je vais simuler un getById en filtrant côté client ou serveur si possible ?
      // Malheureusement le backend ne filtre pas par ID dans get_appointments.
      // Je vais lancer une erreur ou retourner null pour l'instant.
      console.warn("getAppointmentById not implemented in backend controller");
      return null;
    } catch (error) {
      console.error(`Error fetching appointment ${id}:`, error);
      return null;
    }
  },

  getAppointmentsByPatient: async (
    patientId: string
  ): Promise<Appointment[]> => {
    return appointmentService.getAllAppointments({ patientId });
  },

  getAppointmentsByDoctor: async (doctorId: string): Promise<Appointment[]> => {
    return appointmentService.getAllAppointments({ doctorId });
  },

  getAppointmentsCalendar: async (
    year: number,
    month: number
  ): Promise<Appointment[]> => {
    try {
      // Calculer le premier et dernier jour du mois
      const startDate = new Date(year, month - 1, 1);
      const endDate = new Date(year, month, 0, 23, 59, 59); // Dernier jour du mois

      return appointmentService.getAllAppointments({
        startDate: startDate.toISOString(),
        endDate: endDate.toISOString(),
      });
    } catch (error) {
      console.error(`Error fetching calendar for ${year}/${month}:`, error);
      return [];
    }
  },

  createAppointment: async (
    appointment: AppointmentCreateDto
  ): Promise<Appointment | null> => {
    try {
      const adaptedAppointment = adaptAppointmentCreateDto(appointment);
      console.log("Creating appointment with data:", adaptedAppointment);

      const response = await apiClient.post<any>(
        ENDPOINTS.APPOINTMENTS.BASE,
        adaptedAppointment
      );

      console.log("Appointment created successfully:", response);
      return adaptAppointmentFromApi(response);
    } catch (error) {
      console.error("Error creating appointment:", error);
      throw error;
    }
  },

  updateAppointment: async (
    id: string,
    appointment: AppointmentUpdateDto
  ): Promise<Appointment | null> => {
    // Pas de PUT /appointments/{id} dans le backend actuel
    // Seulement DELETE
    console.error("Update not supported by backend");
    return null;
  },

  cancelAppointment: async (
    id: string,
    reason?: string
  ): Promise<Appointment | null> => {
    try {
      // DELETE avec param query cancel_reason
      const queryParams = new URLSearchParams();
      if (reason) queryParams.append("cancel_reason", reason);

      await apiClient.delete<any>(
        `${ENDPOINTS.APPOINTMENTS.DETAIL(id)}?${queryParams.toString()}`
      );
      // Le backend retourne null (204 No Content).
      // On retourne un objet dummy ou null, le frontend doit gérer ça.
      return { id } as Appointment;
    } catch (error) {
      console.error(`Error cancelling appointment ${id}:`, error);
      return null;
    }
  },

  confirmAppointment: async (id: string): Promise<Appointment | null> => {
    // Pas supporté par backend actuel
    return null;
  },

  completeAppointment: async (id: string): Promise<Appointment | null> => {
    // Pas supporté par backend actuel
    return null;
  },
};

export default appointmentService;
