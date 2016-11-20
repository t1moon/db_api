# coding=utf-8

INSERT_THREAD = u'''INSERT INTO thread
                   (forum_slug, title, isClosed, user_email, date, message, slug, isDeleted)
                   VALUES
                   (%s, %s, %s, %s, %s, %s, %s, %s) ;
                '''

SELECT_THREAD_DATA_BY_ID = u'''SELECT date, dislikes, forum_slug, id,
                                   isClosed, isDeleted, likes, message,
                                   likes - dislikes as points, posts,
                                   slug, title, user_email
                            FROM thread
                            WHERE id = %s;
                        '''

SELECT_THREAD_BY_ID = u'''SELECT id
                            FROM thread
                            WHERE id = %s ;
                        '''

SELECT_ALL_THREADS_BY_FORUM_UNSPECIFIED = u'''SELECT date, dislikes, forum_slug,
                                                    id, isClosed, isDeleted,
                                                    likes, message,
                                                    likes - dislikes as points, posts,
                                                    slug, title, user_email
                                            FROM thread
                                            WHERE forum_slug = %s
                                            '''

UPDATE_THREAD_POSTS = u'''UPDATE thread
                         SET posts = posts + %s
                         WHERE id = %s
                      '''

SELECT_THREAD_BY_POST_ID = u'''SELECT thread_id
                                   FROM post
                                   WHERE id = %s
                                '''
# переделать айдишник форума по slug айдишник юзера по email и оптимизировать это
SELECT_THREADS_BY_FORUM_OR_USER = u'''SELECT date, dislikes, forum_slug,
                                            id, isClosed, isDeleted,
                                            likes, message,
                                            likes - dislikes as points, posts,
                                            slug, title, user_email
                                     FROM thread
                                     WHERE {} = %s
                                  '''

UPDATE_THREAD_DELETED_FLAG = u'''UPDATE thread
                                SET isDeleted = {}
                                WHERE id = %s;
                             '''

UPDATE_THREAD_POSTS_DELETED_FLAG = u'''UPDATE post
                                      SET isDeleted = {}
                                      WHERE thread_id = %s
                                   '''

UPDATE_THREAD_SET_IS_CLOSED_FLAG = u'''UPDATE thread
                                       SET isClosed = {}
                                       WHERE id = %s;
                                    '''

UPDATE_THREAD = u'''UPDATE thread
                    SET message = %s,
                        slug = %s
                    WHERE id = %s;
                 '''

UPDATE_THREAD_VOTES = u'''
                        UPDATE thread
                        SET {} = {} + 1
                        WHERE id = %s ;
                        '''


INSERT_SUBSCRIPTION = u'''
                        INSERT INTO subscriptions
                        (thread_id, user_email)
                        VALUES (%s, %s) ;
                    '''

DELETE_SUBSCRIPTION = u'''
                        DELETE FROM subscriptions
                        WHERE thread_id = %s AND user_email = %s ;
                    '''