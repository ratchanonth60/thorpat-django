import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import AuthService from '../../../shared/src/api/auth';
import Input from '../components/common/Input';
import Button from '../components/common/Button';

const ResetPasswordConfirmScreen = () => {
  const { uidb64, token } = useParams();
  const navigate = useNavigate();
  const [newPassword1, setNewPassword1] = useState('');
  const [newPassword2, setNewPassword2] = useState('');
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);

  const handleSubmit = async (event) => {
    event.preventDefault();
    setLoading(true);
    setError(null);
    setSuccess(false);

    if (newPassword1 !== newPassword2) {
      setError('Passwords do not match.');
      setLoading(false);
      return;
    }

    try {
      await AuthService.confirmPasswordReset(uidb64, token, newPassword1, newPassword2);
      setSuccess(true);
      setTimeout(() => {
        navigate('/login');
      }, 3000);
    } catch (err) {
      setError(err.message || 'Failed to reset password.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-50 font-sans">
      <div className="w-full max-w-md p-8 space-y-8 bg-white rounded-lg shadow-lg">
        <h2 className="text-3xl font-bold text-center text-gray-800">Reset Password</h2>
        <p className="text-center text-gray-500">Enter your new password</p>

        <form onSubmit={handleSubmit} className="space-y-6">
          {error && (
            <div className="p-3 text-sm text-red-700 bg-red-100 border border-red-200 rounded-md">
              {error}
            </div>
          )}
          {success && (
            <div className="p-3 text-sm text-green-700 bg-green-100 border border-green-200 rounded-md">
              Password has been reset successfully! Redirecting to login...
            </div>
          )}

          <div>
            <label htmlFor="new-password-1" className="block text-sm font-medium text-gray-700">New Password</label>
            <Input id="new-password-1" type="password" placeholder="Enter new password" value={newPassword1} onChange={(e) => setNewPassword1(e.target.value)} />
          </div>

          <div>
            <label htmlFor="new-password-2" className="block text-sm font-medium text-gray-700">Confirm New Password</label>
            <Input id="new-password-2" type="password" placeholder="Confirm new password" value={newPassword2} onChange={(e) => setNewPassword2(e.target.value)} />
          </div>

          <Button type="submit" disabled={loading}>
            {loading ? 'Resetting...' : 'Reset Password'}
          </Button>
        </form>
      </div>
    </div>
  );
};

export default ResetPasswordConfirmScreen;
