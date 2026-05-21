from firebase_admin_service import get_firestore, init_firebase


def migrate(copy_only=True):
        init_firebase()
        db = get_firestore()
        migrated = []
        for doc in db.collection_group('children').stream():
                parent_ref = getattr(doc.reference, 'parent', None)
                if parent_ref is None:
                        continue
                parent_parent = getattr(parent_ref, 'parent', None)
                if parent_parent is None:
                        continue
                parent_id = parent_parent.id
                data = doc.to_dict() or {}
                child_id = doc.id

                data['parent_id'] = parent_id

                top_ref = db.collection('children').document(child_id)
                top_ref.set(data)
                migrated.append(child_id)
                if not copy_only:
                        try:
                                doc.reference.delete()
                        except Exception:
                                pass
        print(f"Migrated {len(migrated)} children: {migrated}")


if __name__ == '__main__':
        migrate(copy_only=True)
