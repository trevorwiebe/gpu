import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router';
import { useUser, RedirectToSignIn } from '@clerk/clerk-react';
import { useAuthenticateNodeMutation } from '../store';

export default function Setup() {
    const { setupToken } = useParams<{ setupToken: string }>();
    const { isSignedIn, user, isLoaded } = useUser();
    const navigate = useNavigate();

    const [authenticateNode, { isLoading, isSuccess, isError, error }] = useAuthenticateNodeMutation();
    const [hasAttempted, setHasAttempted] = useState(false);

    useEffect(() => {
        // Only attempt authentication once user is loaded and signed in
        if (isLoaded && isSignedIn && user && setupToken && !hasAttempted) {
            setHasAttempted(true);

            authenticateNode({
                userId: user.id,
                setupToken: setupToken
            });
        }
    }, [isLoaded, isSignedIn, user, setupToken, hasAttempted, authenticateNode]);

    // Redirect to hosted page after successful authentication
    useEffect(() => {
        if (isSuccess) {
            const timer = setTimeout(() => {
                navigate('/hosted');
            }, 3000);
            return () => clearTimeout(timer);
        }
    }, [isSuccess, navigate]);

    // Show loading state while Clerk is initializing
    if (!isLoaded) {
        return (
            <div className="flex flex-col items-center justify-center min-h-[60vh]">
                <div className="text-lg">Loading...</div>
            </div>
        );
    }

    // Force sign-in if not authenticated
    if (!isSignedIn) {
        return <RedirectToSignIn forceRedirectUrl={`/setup/${setupToken}`} />;
    }

    // Show error if no setup token provided
    if (!setupToken) {
        return (
            <div className="flex flex-col items-center justify-center min-h-[60vh] max-w-2xl mx-auto px-4">
                <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
                    <h1 className="text-2xl font-bold text-red-800 mb-2">Invalid Setup Link</h1>
                    <p className="text-red-600">No setup token provided in the URL.</p>
                </div>
            </div>
        );
    }

    return (
        <div className="flex flex-col items-center justify-center min-h-[60vh] max-w-2xl mx-auto px-4">
            <div className="bg-white border border-gray-200 rounded-lg p-8 shadow-sm w-full">
                <h1 className="text-3xl font-bold text-gray-900 mb-6 text-center">
                    Node Setup
                </h1>

                {isLoading && (
                    <div className="text-center">
                        <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mb-4"></div>
                        <p className="text-lg text-gray-700">Authenticating your node...</p>
                    </div>
                )}

                {isSuccess && (
                    <div className="bg-green-50 border border-green-200 rounded-lg p-6">
                        <div className="flex items-center justify-center mb-4">
                            <svg className="h-12 w-12 text-green-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                            </svg>
                        </div>
                        <h2 className="text-xl font-semibold text-green-800 mb-2 text-center">
                            Success!
                        </h2>
                        <p className="text-green-700 text-center mb-4">
                            Your node has been successfully connected to your account.
                        </p>
                        <p className="text-green-600 text-sm text-center">
                            Redirecting to your hosted models page...
                        </p>
                    </div>
                )}

                {isError && (
                    <div className="bg-red-50 border border-red-200 rounded-lg p-6">
                        <div className="flex items-center justify-center mb-4">
                            <svg className="h-12 w-12 text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                            </svg>
                        </div>
                        <h2 className="text-xl font-semibold text-red-800 mb-2 text-center">
                            Authentication Failed
                        </h2>
                        <p className="text-red-700 text-center mb-4">
                            {error && 'data' in error && typeof error.data === 'object' && error.data !== null && 'message' in error.data
                                ? String(error.data.message)
                                : 'The setup token may have expired or is invalid. Please generate a new setup link from your node.'}
                        </p>
                        <div className="text-center">
                            <button
                                onClick={() => navigate('/hosted')}
                                className="bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-6 rounded-lg transition-colors"
                            >
                                Go to Hosted Models
                            </button>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}
