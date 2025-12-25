"""
Constants for user authentication and login systems
"""
DEVICE_TYPES = [
    'iPhone 14', 'Samsung Galaxy S23', 'Google Pixel 7',
    'Windows Desktop', 'MacBook Pro', 'iPad', 'Android Tablet',
    'Mobile Web', 'Desktop Web', 'Unknown Device'
]

BROWSERS = [
    'Chrome', 'Safari', 'Firefox', 'Edge', 'Opera', 'Brave', 'Internet Explorer'
]

OPERATING_SYSTEMS = [
    'iOS 16', 'Android 13', 'Windows 11', 'macOS Ventura',
    'Linux', 'Chrome OS', 'Ubuntu', 'Windows 10'
]

LOGIN_METHODS = ['PASSWORD', 'BIOMETRIC', '2FA', 'SSO', 'OTP', 'HARDWARE_TOKEN']

FAILURE_REASONS = [
    'INVALID_PASSWORD', 'EXPIRED_PASSWORD', 'ACCOUNT_LOCKED',
    'DEVICE_NOT_RECOGNIZED', 'LOCATION_SUSPICIOUS', '2FA_FAILED',
    'SESSION_EXPIRED', 'BRUTE_FORCE_ATTEMPT', 'IP_BLOCKED'
]

LOGIN_STATUS = ['SUCCESS', 'FAILED', 'BLOCKED', 'REQUIRES_2FA']