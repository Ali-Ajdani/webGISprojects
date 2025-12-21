using System.Collections.Concurrent;

namespace AuthProject
{
    public static class TokenStore
    {
        public static ConcurrentDictionary<string, bool> Tokens
            = new ConcurrentDictionary<string, bool>();
    }
}
