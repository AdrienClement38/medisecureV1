import React from "react";
import { useAuth } from "../../context/AuthContext";
import Button from "../../components/common/Button/Button";
import { Link } from "react-router-dom";

const ProfilePage: React.FC = () => {
    const { user } = useAuth();

    return (
        <div className="space-y-6">
            <div className="flex justify-between items-center">
                <div>
                    <h1 className="text-2xl font-semibold text-slate-900">Mon Profil</h1>
                    <p className="mt-1 text-slate-500">
                        Consultez vos informations personnelles
                    </p>
                </div>
                <Link to="/settings">
                    <Button variant="outline">Modifier mon profil</Button>
                </Link>
            </div>

            <div className="bg-white shadow rounded-lg overflow-hidden">
                <div className="px-4 py-5 sm:px-6">
                    <h3 className="text-lg leading-6 font-medium text-slate-900">
                        Informations utilisateur
                    </h3>
                    <p className="mt-1 max-w-2xl text-sm text-slate-500">
                        Détails de votre compte MediSecure
                    </p>
                </div>
                <div className="border-t border-slate-200">
                    <dl>
                        <div className="bg-slate-50 px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
                            <dt className="text-sm font-medium text-slate-500">Email</dt>
                            <dd className="mt-1 text-sm text-slate-900 sm:mt-0 sm:col-span-2">
                                {user?.email}
                            </dd>
                        </div>
                        <div className="bg-white px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
                            <dt className="text-sm font-medium text-slate-500">Rôle</dt>
                            <dd className="mt-1 text-sm text-slate-900 sm:mt-0 sm:col-span-2">
                                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-primary-100 text-primary-800">
                                    {user?.role || "Utilisateur"}
                                </span>
                            </dd>
                        </div>
                        <div className="bg-slate-50 px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
                            <dt className="text-sm font-medium text-slate-500">ID Utilisateur</dt>
                            <dd className="mt-1 text-sm text-slate-900 sm:mt-0 sm:col-span-2">
                                {user?.id}
                            </dd>
                        </div>
                    </dl>
                </div>
            </div>
        </div>
    );
};

export default ProfilePage;
