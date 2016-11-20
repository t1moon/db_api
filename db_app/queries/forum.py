SELECT_FORUM_DATA_BY_SHORT_NAME = '''
                                    SELECT id, name, short_name, Users.email, Users.id
                                    FROM Forums INNER JOIN Users
                                    ON Forums.user_id = Users.id
                                    WHERE Forums.short_name = %s;
                                    '''

SELECT_FORUM_DATA_BY_SLUG = '''
                            SELECT id, name, short_name, user
                            FROM Forums
                            WHERE short_name = %s;
                            '''

INSERT_FORUM = '''INSERT INTO Forums
                   (name, short_name, user)
                   VALUES
                   (%s, %s, %s);
               '''

SELECT_FORUM_ID_BY_SLUG = '''
                        SELECT id
                        FROM Forums
                        WHERE short_name = %s ;
                        '''

SELECT_FORUM_PROFILE_BY_SLUG = '''SELECT id, name, short_name, user
                                FROM Forums
                                WHERE short_name = %s ;
                                '''

SELECT_FORUM_PROFILE_BY_ID = '''SELECT id, forum.name, short_name, Users.email, Users.id
                                FROM Forums INNER JOIN Users
                                ON Forums.user = Users.email
                                WHERE Forums.id = %s ;
                                '''
