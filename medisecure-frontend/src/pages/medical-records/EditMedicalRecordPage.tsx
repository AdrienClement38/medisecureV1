import React, { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import Button from "../../components/common/Button/Button";
import InputField from "../../components/common/InputField/InputField";
import toast from "react-hot-toast";

const EditMedicalRecordPage: React.FC = () => {
    const { recordId } = useParams<{ recordId: string }>();
    const navigate = useNavigate();
    const [loading, setLoading] = useState(false);

    // State for form fields
    const [formData, setFormData] = useState({
        title: "",
        date: "",
        type: "",
        doctor: ""
    });

    useEffect(() => {
        // Simulate fetching data
        setFormData({
            title: "Consultation initiale",
            date: "2023-01-15",
            type: "Consultation",
            doctor: "Dr. Jean Dupont"
        });
    }, [recordId]);

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const { name, value } = e.target;
        setFormData(prev => ({ ...prev, [name]: value }));
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);

        // Simulate API call
        setTimeout(() => {
            setLoading(false);
            toast.success("Dossier médical mis à jour");
            navigate(-1);
        }, 1000);
    };

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <h1 className="text-2xl font-semibold text-slate-900">
                    Modifier le dossier médical #{recordId}
                </h1>
                <Button variant="outline" onClick={() => navigate(-1)}>
                    Annuler
                </Button>
            </div>

            <div className="card">
                <form onSubmit={handleSubmit} className="space-y-6">
                    <div className="grid grid-cols-1 gap-6">
                        <InputField
                            id="title"
                            name="title"
                            label="Titre"
                            value={formData.title}
                            onChange={handleChange}
                            required
                        />
                        <InputField
                            id="date"
                            name="date"
                            label="Date"
                            type="date"
                            value={formData.date}
                            onChange={handleChange}
                            required
                        />
                        <InputField
                            id="type"
                            name="type"
                            label="Type"
                            value={formData.type}
                            onChange={handleChange}
                            required
                        />
                        <InputField
                            id="doctor"
                            name="doctor"
                            label="Médecin"
                            value={formData.doctor}
                            onChange={handleChange}
                            required
                        />
                    </div>

                    <div className="flex justify-end">
                        <Button type="submit" variant="primary" isLoading={loading}>
                            Enregistrer
                        </Button>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default EditMedicalRecordPage;
