<?php

/**
 * Key hash passwords
 *
 * @author Pablo Morales
 */
class PassHash {

    // blowfish
    private static $algo = '$2a';
    // cost parameter
    private static $cost = '$10';

    // mainly for internal use
    public static function uniqueSalt() {
        return substr(sha1(mt_rand()), 0, 22);
    }

    // this will be used to generate a hash
    public static function hash($password) {
        return crypt($password, self::$algo . self::$cost . '$' . self::uniqueSalt());
    }

    // this will be used to compare a password against a hash
    public static function checkPassword($hash, $password) {
        $full_salt  = substr($hash, 0, 29);
        $new_hash   = crypt($password, $full_salt);
        return ($hash == $new_hash);
    }
}
?>